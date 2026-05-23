"""Lidarr response models — artists, albums, tracks."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Artist(BaseModel):
    """A Lidarr artist resource."""

    id: int | None = Field(default=None, description="Lidarr artist ID.")
    artist_name: str = Field(default="", description="Artist name.", alias="artistName")
    foreign_artist_id: str | None = Field(default=None, description="MusicBrainz ID.", alias="foreignArtistId")
    monitored: bool = Field(default=False, description="Whether monitored.")
    quality_profile_id: int | None = Field(default=None, description="Quality profile ID.", alias="qualityProfileId")
    path: str | None = Field(default=None, description="Filesystem path.")
    overview: str | None = Field(default=None, description="Artist biography.")
    genres: list[str] = Field(default_factory=list, description="Genre list.")
    tags: list[int] = Field(default_factory=list, description="Tag IDs.")

    model_config = {"populate_by_name": True, "extra": "ignore"}


class Album(BaseModel):
    """A Lidarr album resource."""

    id: int | None = Field(default=None, description="Album ID.")
    title: str = Field(default="", description="Album title.")
    artist_id: int | None = Field(default=None, description="Parent artist ID.", alias="artistId")
    foreign_album_id: str | None = Field(default=None, description="MusicBrainz release ID.", alias="foreignAlbumId")
    release_date: str | None = Field(default=None, description="Release date.", alias="releaseDate")
    monitored: bool = Field(default=False, description="Whether monitored.")
    album_type: str | None = Field(default=None, description="Album type (Album, EP, Single, …).", alias="albumType")
    track_count: int | None = Field(default=None, description="Number of tracks.")

    model_config = {"populate_by_name": True, "extra": "ignore"}


class ArtistListResult(BaseModel):
    """Wrapper for artist/album list responses."""

    success: bool = Field(description="Whether the operation succeeded.")
    message: str = Field(default="", description="Human-readable summary.")
    data: list[Artist] | list[Album] | list[dict[str, Any]] = Field(default_factory=list)
    total: int | None = Field(default=None, description="Total count when applicable.")
