"""Nightly agent — refresh catalog for all portfolio repos."""

from __future__ import annotations

import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

REPO_ROOT = Path(__file__).parent.parent


def sync_self() -> None:
    """Generate catalog-info.yaml for this repo."""
    from catalogsync.core.config import SyncConfig
    from catalogsync.scanners.repo import scan_repo
    from catalogsync.writers.yaml_writer import build_entity, write_catalog_yaml

    config = SyncConfig()
    scan = scan_repo(REPO_ROOT, "brianpelow/service-catalog-sync")
    entity = build_entity(scan, config)
    out = REPO_ROOT / "catalog-info.yaml"
    write_catalog_yaml(entity, out)
    print(f"[agent] Generated catalog-info.yaml -> {out}")


def update_sync_report() -> None:
    """Write a sync report to docs."""
    from catalogsync.core.config import SyncConfig
    from catalogsync.scanners.repo import scan_repo
    from catalogsync.writers.yaml_writer import build_entity

    config = SyncConfig()
    scan = scan_repo(REPO_ROOT, "brianpelow/service-catalog-sync")
    entity = build_entity(scan, config)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "date": date.today().isoformat(),
        "repo": scan.name,
        "language": scan.language,
        "framework": scan.framework,
        "owner": scan.owner,
        "tech_stack": scan.tech_stack,
        "tags": scan.tags,
        "entity_kind": entity.kind,
        "entity_type": entity.spec.type,
        "lifecycle": entity.spec.lifecycle,
    }

    out = REPO_ROOT / "docs" / "sync-report.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(report, indent=2))
    print(f"[agent] Sync report updated -> {out}")


def refresh_changelog() -> None:
    changelog = REPO_ROOT / "CHANGELOG.md"
    if not changelog.exists():
        return
    today = date.today().isoformat()
    content = changelog.read_text()
    if today not in content:
        content = content.replace("## [Unreleased]", f"## [Unreleased]\n\n_Last synced: {today}_", 1)
        changelog.write_text(content)
    print("[agent] Refreshed CHANGELOG timestamp")


if __name__ == "__main__":
    print(f"[agent] Starting nightly agent - {date.today().isoformat()}")
    sync_self()
    update_sync_report()
    refresh_changelog()
    print("[agent] Done.")