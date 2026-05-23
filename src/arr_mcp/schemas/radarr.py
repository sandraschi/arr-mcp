"""Radarr response models — movies, movie files, quality profiles."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Movie(BaseModel):
    """A Radarr movie resource."""

    id: int | None = Field(default=None, description="Radarr movie ID.")
    title: str = Field(default="", description="Movie title.")
    tmdb_id: int | None = Field(default=None, description="TMDB ID.", alias="tmdbId")
    imdb_id: str | None = Field(default=None, description="IMDB ID.", alias="imdbId")
    year: int | None = Field(default=None, description="Release year.")
    monitored: bool = Field(default=False, description="Whether Radarr monitors this movie.")
    has_file: bool | None = Field(default=None, description="Whether a movie file exists.", alias="hasFile")
    quality_profile_id: int | None = Field(default=None, description="Quality profile ID.", alias="qualityProfileId")
    path: str | None = Field(default=None, description="Filesystem path.")
    overview: str | None = Field(default=None, description="Plot overview.")
    genres: list[str] = Field(default_factory=list, description="Genre list.")
    tags: list[int] = Field(default_factory=list, description="Tag IDs.")

    model_config = {"populate_by_name": True, "extra": "ignore"}


class MovieListResult(BaseModel):
    """Wrapper for movie list responses."""

    success: bool = Field(description="Whether the operation succeeded.")
    message: str = Field(default="", description="Human-readable summary.")
    data: list[Movie] | list[dict[str, Any]] = Field(default_factory=list, description="Movies or raw data.")
    total: int | None = Field(default=None, description="Total count when applicable.")
