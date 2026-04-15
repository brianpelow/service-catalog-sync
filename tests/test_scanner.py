"""Tests for repository scanner."""

import tempfile
from pathlib import Path
from catalogsync.scanners.repo import scan_repo


def test_scan_empty_repo() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        result = scan_repo(Path(tmpdir))
        assert result.name == Path(tmpdir).name
        assert result.language == "unknown"
        assert result.owner == "platform-team"


def test_scan_detects_python() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "pyproject.toml").write_text("[project]\nname = \"test\"\n")
        result = scan_repo(Path(tmpdir))
        assert result.language == "Python"


def test_scan_detects_owner_from_codeowners() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        (path / ".github").mkdir()
        (path / ".github" / "CODEOWNERS").write_text("* @payments-team\n")
        result = scan_repo(path)
        assert result.owner == "payments-team"


def test_scan_detects_ci() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        (path / ".github" / "workflows").mkdir(parents=True)
        (path / ".github" / "workflows" / "ci.yml").write_text("name: CI\n")
        result = scan_repo(path)
        assert result.has_ci is True


def test_scan_detects_dockerfile() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "Dockerfile").write_text("FROM python:3.12\n")
        result = scan_repo(Path(tmpdir))
        assert result.has_dockerfile is True


def test_scan_extracts_description() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        (path / "README.md").write_text(
            "# My Service\n\n> A payments processing service for regulated industries.\n\n## Overview\n"
        )
        result = scan_repo(path)
        assert len(result.description) > 10


def test_scan_builds_tags() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir)
        (path / "pyproject.toml").write_text('[project]\ndependencies = ["fastapi>=0.111.0"]\n')
        result = scan_repo(path)
        assert "python" in result.tags