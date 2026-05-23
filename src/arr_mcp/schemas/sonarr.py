"""Sonarr response models — series, episodes, episode files."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Series(BaseModel):
    """A Sonarr series resource."""

    id: int | None = Field(default=None, description="Sonarr series ID.")
    title: str = Field(default="", description="Series title.")
    tvdb_id: int | None = Field(default=None, description="TVDB ID.", alias="tvdbId")
    tv_maze_id: int | None = Field(default=None, description="TVmaze ID.", alias="tvMazeId")
    year: int | None = Field(default=None, description="First aired year.")
    monitored: bool = Field(default=False, description="Whether Sonarr monitors this series.")
    season_count: int | None = Field(default=None, description="Number of seasons.")
    path: str | None = Field(default=None, description="Filesystem path.")
    overview: str | None = Field(default=None, description="Plot overview.")
    genres: list[str] = Field(default_factory=list, description="Genre list.")
    tags: list[int] = Field(default_factory=list, description="Tag IDs.")

    model_config = {"populate_by_name": True, "extra": "ignore"}


class Episode(BaseModel):
    """A Sonarr episode resource."""

    id: int | None = Field(default=None, description="Episode ID.")
    series_id: int | None = Field(default=None, description="Parent series ID.", alias="seriesId")
    season_number: int | None = Field(default=None, description="Season number.", alias="seasonNumber")
    episode_number: int | None = Field(default=None, description="Episode number.", alias="episodeNumber")
    title: str = Field(default="", description="Episode title.")
    overview: str | None = Field(default=None, description="Episode overview.")
    monitored: bool = Field(default=False, description="Whether monitored.")
    has_file: bool | None = Field(default=None, description="Whether an episode file exists.", alias="hasFile")
    air_date: str | None = Field(default=None, description="Air date.", alias="airDate")
    air_date_utc: str | None = Field(default=None, description="Air date UTC.", alias="airDateUtc")

    model_config = {"populate_by_name": True, "extra": "ignore"}


class SeriesListResult(BaseModel):
    """Wrapper for series/episode list responses."""

    success: bool = Field(description="Whether the operation succeeded.")
    message: str = Field(default="", description="Human-readable summary.")
    data: list[Series] | list[Episode] | list[dict[str, Any]] = Field(default_factory=list)
    total: int | None = Field(default=None, description="Total count when applicable.")
