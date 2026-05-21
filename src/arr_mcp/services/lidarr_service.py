"""Lidarr HTTP client (Music).

Extends :class:`BaseArrClient` with Lidarr-specific endpoints for artist
management, albums, tracks, and MusicBrainz-based lookup.
"""

from __future__ import annotations

from typing import Any

from arr_mcp.constants import DEFAULT_TIMEOUT, LIDARR_API_PATH
from arr_mcp.services.base import BaseArrClient


class LidarrClient(BaseArrClient):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        super().__init__(
            name="Lidarr",
            base_url=base_url,
            api_key=api_key,
            api_path=LIDARR_API_PATH,
            timeout=timeout,
        )

    # ── artists ───────────────────────────────────────────────────

    async def get_artists(self, mb_id: str | None = None) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if mb_id:
            params["mbId"] = mb_id
        return await self._get(f"{self.api_path}/artist", **params)  # type: ignore[return-value]

    async def get_artist(self, artist_id: int) -> dict[str, Any]:
        return await self._get(f"{self.api_path}/artist/{artist_id}")  # type: ignore[return-value]

    async def lookup_artist(self, term: str) -> list[dict[str, Any]]:
        return await self._get(f"{self.api_path}/artist/lookup", term=term)  # type: ignore[return-value]

    async def add_artist(
        self,
        foreign_artist_id: str,
        quality_profile_id: int,
        root_folder_path: str,
        monitored: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "foreignArtistId": foreign_artist_id,
            "qualityProfileId": quality_profile_id,
            "rootFolderPath": root_folder_path,
            "monitored": monitored,
            **kwargs,
        }
        return await self._post(f"{self.api_path}/artist", json=payload)

    async def delete_artist(self, artist_id: int, delete_files: bool = False) -> dict[str, Any]:
        return await self._delete(  # type: ignore[return-value]
            f"{self.api_path}/artist/{artist_id}",
            deleteFiles=delete_files,
        )

    async def update_artist(self, artist_id: int, **fields: Any) -> dict[str, Any]:
        artist = await self.get_artist(artist_id)
        artist.update(fields)
        return await self._put(f"{self.api_path}/artist/{artist_id}", json=artist)

    # ── albums ────────────────────────────────────────────────────

    async def get_albums(
        self,
        artist_id: int | None = None,
        include_all_artist_albums: bool = False,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if artist_id:
            params["artistId"] = artist_id
        params["includeAllArtistAlbums"] = include_all_artist_albums
        return await self._get(f"{self.api_path}/album", **params)  # type: ignore[return-value]

    async def get_album(self, album_id: int) -> dict[str, Any]:
        return await self._get(f"{self.api_path}/album/{album_id}")  # type: ignore[return-value]

    async def lookup_album(self, term: str) -> list[dict[str, Any]]:
        return await self._get(f"{self.api_path}/album/lookup", term=term)  # type: ignore[return-value]

    async def update_album(self, album_id: int, **fields: Any) -> dict[str, Any]:
        album = await self.get_album(album_id)
        album.update(fields)
        return await self._put(f"{self.api_path}/album/{album_id}", json=album)

    async def set_albums_monitored(self, album_ids: list[int], monitored: bool) -> dict[str, Any]:
        return await self._put(  # type: ignore[return-value]
            f"{self.api_path}/album/monitor",
            json={"albumIds": album_ids, "monitored": monitored},
        )

    async def delete_album(self, album_id: int, delete_files: bool = False) -> dict[str, Any]:
        return await self._delete(  # type: ignore[return-value]
            f"{self.api_path}/album/{album_id}",
            deleteFiles=delete_files,
        )

    # ── track files ───────────────────────────────────────────────

    async def get_track_files(self, artist_id: int | None = None) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if artist_id:
            params["artistId"] = artist_id
        return await self._get(f"{self.api_path}/trackfile", **params)  # type: ignore[return-value]

    # ── metadata profiles ─────────────────────────────────────────

    async def get_metadata_profiles(self) -> list[dict[str, Any]]:
        return await self._get(f"{self.api_path}/metadataprofile")  # type: ignore[return-value]
