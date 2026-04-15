"""Tests for catalog entity models."""

from catalogsync.models.entity import CatalogEntity, EntityMetadata, ComponentSpec, RepoScan


def test_entity_metadata_defaults() -> None:
    meta = EntityMetadata(name="test-service")
    assert meta.description == ""
    assert meta.tags == []
    assert meta.annotations == {}


def test_component_spec_defaults() -> None:
    spec = ComponentSpec()
    assert spec.type == "service"
    assert spec.lifecycle == "production"
    assert spec.owner == "platform-team"


def test_catalog_entity_to_yaml_dict() -> None:
    entity = CatalogEntity(
        metadata=EntityMetadata(name="payments-service", description="Payments processor"),
        spec=ComponentSpec(owner="payments-team", system="payments-platform"),
    )
    d = entity.to_yaml_dict()
    assert d["apiVersion"] == "backstage.io/v1alpha1"
    assert d["kind"] == "Component"
    assert d["metadata"]["name"] == "payments-service"
    assert d["spec"]["owner"] == "payments-team"
    assert d["spec"]["system"] == "payments-platform"


def test_catalog_entity_yaml_excludes_empty_system() -> None:
    entity = CatalogEntity(
        metadata=EntityMetadata(name="test"),
        spec=ComponentSpec(system=""),
    )
    d = entity.to_yaml_dict()
    assert "system" not in d["spec"]


def test_repo_scan_defaults() -> None:
    scan = RepoScan(name="test-repo", path="/tmp/test")
    assert scan.language == "unknown"
    assert scan.has_ci is False
    assert scan.tags == []