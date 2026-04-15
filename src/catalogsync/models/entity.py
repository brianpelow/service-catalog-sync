"""Backstage catalog entity models."""

from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Optional


class EntityMetadata(BaseModel):
    """Backstage entity metadata."""

    name: str
    description: str = ""
    annotations: dict[str, str] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    labels: dict[str, str] = Field(default_factory=dict)


class ComponentSpec(BaseModel):
    """Backstage Component spec."""

    type: str = "service"
    lifecycle: str = "production"
    owner: str = "platform-team"
    system: str = ""
    depends_on: list[str] = Field(default_factory=list)
    provides_apis: list[str] = Field(default_factory=list)


class CatalogEntity(BaseModel):
    """A Backstage catalog entity."""

    api_version: str = "backstage.io/v1alpha1"
    kind: str = "Component"
    metadata: EntityMetadata
    spec: ComponentSpec

    def to_yaml_dict(self) -> dict:
        d: dict = {
            "apiVersion": self.api_version,
            "kind": self.kind,
            "metadata": {
                "name": self.metadata.name,
                "description": self.metadata.description,
            },
            "spec": {
                "type": self.spec.type,
                "lifecycle": self.spec.lifecycle,
                "owner": self.spec.owner,
            },
        }
        if self.metadata.annotations:
            d["metadata"]["annotations"] = self.metadata.annotations
        if self.metadata.tags:
            d["metadata"]["tags"] = self.metadata.tags
        if self.spec.system:
            d["spec"]["system"] = self.spec.system
        if self.spec.depends_on:
            d["spec"]["dependsOn"] = self.spec.depends_on
        return d


class RepoScan(BaseModel):
    """Results of scanning a repository."""

    name: str
    path: str
    language: str = "unknown"
    framework: str = ""
    tech_stack: list[str] = Field(default_factory=list)
    owner: str = ""
    description: str = ""
    has_api: bool = False
    has_dockerfile: bool = False
    has_ci: bool = False
    lifecycle: str = "production"
    github_slug: str = ""
    tags: list[str] = Field(default_factory=list)