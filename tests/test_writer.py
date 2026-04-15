"""Tests for YAML writer."""

import tempfile
from pathlib import Path
from catalogsync.core.config import SyncConfig
from catalogsync.models.entity import RepoScan
from catalogsync.writers.yaml_writer import build_entity, write_catalog_yaml, generate_catalog_yaml_string


def make_scan(**kwargs) -> RepoScan:
    defaults = {
        "name": "payments-service",
        "path": "/tmp/payments",
        "language": "Python",
        "framework": "FastAPI",
        "owner": "payments-team",
        "github_slug": "org/payments-service",
        "tags": ["python", "fastapi"],
        "lifecycle": "production",
    }
    defaults.update(kwargs)
    return RepoScan(**defaults)


def test_build_entity_service_type() -> None:
    config = SyncConfig()
    scan = make_scan(name="payments-service")
    entity = build_entity(scan, config)
    assert entity.spec.type == "service"


def test_build_entity_library_type() -> None:
    config = SyncConfig()
    scan = make_scan(name="payments-sdk")
    entity = build_entity(scan, config)
    assert entity.spec.type == "library"


def test_build_entity_preserves_owner() -> None:
    config = SyncConfig()
    scan = make_scan(owner="trading-team")
    entity = build_entity(scan, config)
    assert entity.spec.owner == "trading-team"


def test_build_entity_uses_default_owner() -> None:
    config = SyncConfig(default_owner="platform-team")
    scan = make_scan(owner="")
    entity = build_entity(scan, config)
    assert entity.spec.owner == "platform-team"


def test_generate_yaml_string() -> None:
    config = SyncConfig()
    scan = make_scan()
    entity = build_entity(scan, config)
    yaml_str = generate_catalog_yaml_string(entity)
    assert "apiVersion" in yaml_str
    assert "payments-service" in yaml_str


def test_write_catalog_yaml() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        config = SyncConfig()
        scan = make_scan()
        entity = build_entity(scan, config)
        out = Path(tmpdir) / "catalog-info.yaml"
        result = write_catalog_yaml(entity, out)
        assert result.exists()
        content = result.read_text()
        assert "payments-service" in content
        assert "apiVersion" in content