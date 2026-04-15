"""Catalog YAML writer."""

from __future__ import annotations

from pathlib import Path
import yaml

from catalogsync.models.entity import CatalogEntity, EntityMetadata, ComponentSpec, RepoScan
from catalogsync.core.config import SyncConfig


def build_entity(scan: RepoScan, config: SyncConfig) -> CatalogEntity:
    """Build a Backstage CatalogEntity from a repo scan."""
    annotations: dict[str, str] = {
        "github.com/project-slug": scan.github_slug,
        "backstage.io/techdocs-ref": "dir:.",
    }
    if scan.has_ci:
        annotations["backstage.io/ci-cd"] = "github-actions"

    metadata = EntityMetadata(
        name=scan.name,
        description=scan.description or f"A {config.industry} engineering service",
        annotations=annotations,
        tags=scan.tags,
    )

    component_type = "service"
    if "library" in scan.name or "sdk" in scan.name or "client" in scan.name:
        component_type = "library"
    elif "cli" in scan.name or "tool" in scan.name:
        component_type = "tool"
    elif "mcp" in scan.name:
        component_type = "service"

    spec = ComponentSpec(
        type=component_type,
        lifecycle=scan.lifecycle,
        owner=scan.owner or config.default_owner,
        system=config.default_system,
    )

    return CatalogEntity(metadata=metadata, spec=spec)


def write_catalog_yaml(entity: CatalogEntity, output_path: Path) -> Path:
    """Write catalog entity to a YAML file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        yaml.dump(entity.to_yaml_dict(), f, default_flow_style=False, sort_keys=False)
    return output_path


def generate_catalog_yaml_string(entity: CatalogEntity) -> str:
    """Generate catalog YAML as a string."""
    return yaml.dump(entity.to_yaml_dict(), default_flow_style=False, sort_keys=False)