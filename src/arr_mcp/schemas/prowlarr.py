"""Prowlarr response models — indexers, applications, search results."""

from __future__ import annotations

from pydantic import BaseModel, Field


class Indexer(BaseModel):
    """A Prowlarr indexer resource."""

    id: int | None = Field(default=None, description="Indexer ID.")
    name: str = Field(default="", description="Indexer display name.")
    protocol: str | None = Field(default=None, description="Protocol (usenet / torrent).")
    priority: int = Field(default=25, description="Indexer priority.")
    enable_rss: bool = Field(default=True, description="RSS enabled.", alias="enableRss")
    enable_search: bool = Field(default=True, description="Search enabled.", alias="enableSearch")
    status: str | None = Field(default=None, description="Indexer status.")
    config_contract: str | None = Field(default=None, description="Implementation contract name.")
    tags: list[int] = Field(default_factory=list, description="Tag IDs.")

    model_config = {"populate_by_name": True, "extra": "ignore"}


class ProwlarrApp(BaseModel):
    """A Prowlarr application (connected *arr instance)."""

    id: int | None = Field(default=None, description="Application ID.")
    name: str = Field(default="", description="Application name.")
    app_type: str | None = Field(default=None, description="Type e.g. Radarr, Sonarr.")
    sync_level: str | None = Field(default=None, description="Sync level.")
    enabled: bool = Field(default=True, description="Whether the app sync is active.")

    model_config = {"populate_by_name": True, "extra": "ignore"}


class ProwlarrSearchResult(BaseModel):
    """A single search result from Prowlarr indexers."""

    title: str = Field(default="", description="Release title.")
    guid: str = Field(default="", description="Unique release GUID.")
    indexer: str | None = Field(default=None, description="Source indexer name.")
    indexer_id: int | None = Field(default=None, description="Source indexer ID.")
    size: int | None = Field(default=None, description="Release size in bytes.")
    seeders: int | None = Field(default=None, description="Seeders (torrent only).")
    leechers: int | None = Field(default=None, description="Leechers (torrent only).")
    grabs: int | None = Field(default=None, description="Grabs.")
    protocol: str | None = Field(default=None, description="usenet or torrent.")
    indexer_flags: list[str] = Field(default_factory=list, description="Indexer flags.")
    download_url: str | None = Field(default=None, description="Download URL.")
    info_url: str | None = Field(default=None, description="Info URL.")
    pub_date: str | None = Field(default=None, description="Publication date.")
    categories: list[int] = Field(default_factory=list, description="Category IDs.")

    model_config = {"populate_by_name": True, "extra": "ignore"}
