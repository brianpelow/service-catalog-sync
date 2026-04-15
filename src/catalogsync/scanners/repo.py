"""Repository scanner — infers language, framework, and tech stack."""

from __future__ import annotations

import re
from pathlib import Path
from catalogsync.models.entity import RepoScan


LANGUAGE_INDICATORS = {
    "Python": ["pyproject.toml", "setup.py", "requirements.txt", "Pipfile"],
    "TypeScript": ["tsconfig.json", "package.json"],
    "JavaScript": ["package.json"],
    "Go": ["go.mod", "go.sum"],
    "Java": ["pom.xml", "build.gradle"],
    "Rust": ["Cargo.toml"],
}

FRAMEWORK_INDICATORS = {
    "FastAPI": ["fastapi"],
    "Django": ["django"],
    "Flask": ["flask"],
    "Next.js": ["next.config", "next"],
    "React": ["react"],
    "Spring Boot": ["spring-boot"],
    "LangGraph": ["langgraph"],
    "FastMCP": ["fastmcp"],
}

TECH_STACK_INDICATORS = {
    "PostgreSQL": ["psycopg", "asyncpg", "postgres"],
    "Redis": ["redis"],
    "Kafka": ["kafka", "confluent"],
    "Docker": ["dockerfile", "docker-compose"],
    "Kubernetes": ["kubernetes", "helm", "k8s"],
    "Terraform": ["terraform", ".tf"],
    "GitHub Actions": [".github/workflows"],
    "Anthropic": ["anthropic", "claude"],
    "MCP": ["fastmcp", "mcp"],
}


def scan_repo(repo_path: Path, github_slug: str = "") -> RepoScan:
    """Scan a repository and infer metadata."""
    name = repo_path.name
    description = _extract_description(repo_path)
    language = _detect_language(repo_path)
    framework = _detect_framework(repo_path)
    tech_stack = _detect_tech_stack(repo_path)
    owner = _detect_owner(repo_path)
    lifecycle = _detect_lifecycle(repo_path)
    tags = _build_tags(language, framework, tech_stack)

    return RepoScan(
        name=name,
        path=str(repo_path),
        language=language,
        framework=framework,
        tech_stack=tech_stack,
        owner=owner,
        description=description,
        has_api=_has_api(repo_path),
        has_dockerfile=(repo_path / "Dockerfile").exists() or (repo_path / "docker-compose.yml").exists(),
        has_ci=(repo_path / ".github" / "workflows").exists(),
        lifecycle=lifecycle,
        github_slug=github_slug or f"brianpelow/{name}",
        tags=tags,
    )


def _extract_description(repo_path: Path) -> str:
    readme = repo_path / "README.md"
    if not readme.exists():
        return ""
    lines = readme.read_text(errors="ignore").splitlines()
    for line in lines[1:6]:
        stripped = line.strip().lstrip(">").strip()
        if len(stripped) > 20 and not stripped.startswith("#") and not stripped.startswith("!"):
            return stripped[:200]
    return ""


def _detect_language(repo_path: Path) -> str:
    for lang, indicators in LANGUAGE_INDICATORS.items():
        for indicator in indicators:
            if (repo_path / indicator).exists():
                return lang
    return "unknown"


def _detect_framework(repo_path: Path) -> str:
    all_text = _collect_dep_text(repo_path)
    for framework, keywords in FRAMEWORK_INDICATORS.items():
        if any(kw.lower() in all_text for kw in keywords):
            return framework
    return ""


def _detect_tech_stack(repo_path: Path) -> list[str]:
    all_text = _collect_dep_text(repo_path)
    stack = []
    for tech, keywords in TECH_STACK_INDICATORS.items():
        if any(kw.lower() in all_text for kw in keywords):
            stack.append(tech)
    return stack


def _collect_dep_text(repo_path: Path) -> str:
    parts = []
    for filename in ["pyproject.toml", "requirements.txt", "package.json", "go.mod", "Cargo.toml"]:
        f = repo_path / filename
        if f.exists():
            parts.append(f.read_text(errors="ignore").lower())
    workflows_path = repo_path / ".github" / "workflows"
    if workflows_path.exists():
        parts.append("github actions")
    if (repo_path / "Dockerfile").exists():
        parts.append("dockerfile docker")
    return " ".join(parts)


def _detect_owner(repo_path: Path) -> str:
    codeowners = repo_path / ".github" / "CODEOWNERS"
    if codeowners.exists():
        content = codeowners.read_text(errors="ignore")
        match = re.search(r"@([\w/-]+)", content)
        if match:
            owner = match.group(1)
            if "/" in owner:
                return owner.split("/")[-1]
            return owner
    return "platform-team"


def _detect_lifecycle(repo_path: Path) -> str:
    readme = repo_path / "README.md"
    if readme.exists():
        content = readme.read_text(errors="ignore").lower()
        if "deprecated" in content or "archived" in content:
            return "deprecated"
        if "experimental" in content or "alpha" in content:
            return "experimental"
    return "production"


def _has_api(repo_path: Path) -> bool:
    patterns = ["openapi", "swagger", "api.yaml", "api.json"]
    for f in repo_path.rglob("*"):
        if any(p in f.name.lower() for p in patterns):
            return True
    return False


def _build_tags(language: str, framework: str, tech_stack: list[str]) -> list[str]:
    tags = []
    if language and language != "unknown":
        tags.append(language.lower())
    if framework:
        tags.append(framework.lower().replace(" ", "-").replace(".", ""))
    for tech in tech_stack[:3]:
        tags.append(tech.lower().replace(" ", "-"))
    return tags[:8]