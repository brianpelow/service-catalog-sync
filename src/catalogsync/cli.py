"""service-catalog-sync CLI entry point."""

from __future__ import annotations

from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from catalogsync.core.config import SyncConfig
from catalogsync.scanners.repo import scan_repo
from catalogsync.writers.yaml_writer import build_entity, write_catalog_yaml, generate_catalog_yaml_string

app = typer.Typer(name="catalog-sync", help="Automated Backstage catalog hydration.")
console = Console()


@app.command("scan")
def scan(
    path: str = typer.Argument(".", help="Path to repository"),
    github_slug: str = typer.Option("", "--slug", help="GitHub org/repo slug"),
) -> None:
    """Scan a repository and display inferred metadata."""
    config = SyncConfig.from_env()
    result = scan_repo(Path(path), github_slug)

    console.print(Panel.fit(
        f"Name: [cyan]{result.name}[/cyan]\n"
        f"Language: [yellow]{result.language}[/yellow]\n"
        f"Framework: {result.framework or 'none detected'}\n"
        f"Owner: [green]{result.owner}[/green]\n"
        f"Lifecycle: {result.lifecycle}\n"
        f"Tech stack: {', '.join(result.tech_stack) or 'none detected'}\n"
        f"Tags: {', '.join(result.tags) or 'none'}\n"
        f"Has CI: {result.has_ci} | Has API: {result.has_api} | Has Docker: {result.has_dockerfile}",
        title=f"Scan: {path}",
    ))


@app.command("generate")
def generate(
    path: str = typer.Argument(".", help="Path to repository"),
    output: str = typer.Option("", "--output", "-o", help="Output file path"),
    github_slug: str = typer.Option("", "--slug", help="GitHub org/repo slug"),
    preview: bool = typer.Option(False, "--preview", help="Preview without writing"),
) -> None:
    """Generate catalog-info.yaml for a repository."""
    config = SyncConfig.from_env()
    scan = scan_repo(Path(path), github_slug)
    entity = build_entity(scan, config)
    yaml_content = generate_catalog_yaml_string(entity)

    if preview:
        console.print(Syntax(yaml_content, "yaml", theme="monokai"))
        return

    out_path = Path(output) if output else Path(path) / "catalog-info.yaml"
    write_catalog_yaml(entity, out_path)
    console.print(f"[green]✓[/green] Generated [cyan]{out_path}[/cyan]")
    console.print(Syntax(yaml_content, "yaml", theme="monokai"))


@app.command("sync")
def sync(
    path: str = typer.Argument(".", help="Path to repository"),
    github_slug: str = typer.Option("", "--slug", "-r", help="GitHub org/repo slug"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without pushing"),
) -> None:
    """Scan, generate, and write catalog-info.yaml to the repository."""
    config = SyncConfig.from_env()
    scan = scan_repo(Path(path), github_slug)
    entity = build_entity(scan, config)
    yaml_content = generate_catalog_yaml_string(entity)

    if dry_run:
        console.print("[dim]Dry run — no files written[/dim]")
        console.print(Syntax(yaml_content, "yaml", theme="monokai"))
        return

    out_path = Path(path) / "catalog-info.yaml"
    write_catalog_yaml(entity, out_path)
    console.print(f"[green]✓[/green] catalog-info.yaml written to [cyan]{out_path}[/cyan]")


@app.command("batch")
def batch(
    path: str = typer.Argument(".", help="Directory containing repos"),
    limit: int = typer.Option(20, "--limit", "-n"),
    dry_run: bool = typer.Option(False, "--dry-run"),
) -> None:
    """Generate catalog-info.yaml for all repos in a directory."""
    config = SyncConfig.from_env()
    base = Path(path)
    repos = [d for d in base.iterdir() if d.is_dir() and not d.name.startswith(".")][:limit]

    table = Table(title="Catalog sync", border_style="dim")
    table.add_column("Repo", style="cyan")
    table.add_column("Language", style="yellow")
    table.add_column("Owner", style="green")
    table.add_column("Written")

    for repo_dir in sorted(repos):
        s = scan_repo(repo_dir)
        entity = build_entity(s, config)
        written = "dry run"
        if not dry_run:
            write_catalog_yaml(entity, repo_dir / "catalog-info.yaml")
            written = "[green]✓[/green]"
        table.add_row(repo_dir.name, s.language, s.owner, written)

    console.print(table)


def main() -> None:
    app()


if __name__ == "__main__":
    main()