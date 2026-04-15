"""Configuration for service-catalog-sync."""

from __future__ import annotations

import os
from pydantic import BaseModel, Field


class SyncConfig(BaseModel):
    """Runtime configuration for service-catalog-sync."""

    github_token: str = Field("", description="GitHub API token")
    backstage_url: str = Field("", description="Backstage instance URL")
    backstage_token: str = Field("", description="Backstage API token")
    default_owner: str = Field("platform-team", description="Default owner if not detected")
    default_lifecycle: str = Field("production", description="Default lifecycle")
    default_system: str = Field("", description="Default system")
    industry: str = Field("fintech", description="Industry context")

    @classmethod
    def from_env(cls) -> "SyncConfig":
        return cls(
            github_token=os.environ.get("GITHUB_TOKEN", ""),
            backstage_url=os.environ.get("BACKSTAGE_URL", ""),
            backstage_token=os.environ.get("BACKSTAGE_TOKEN", ""),
            industry=os.environ.get("SYNC_INDUSTRY", "fintech"),
        )

    @property
    def has_github(self) -> bool:
        return bool(self.github_token)