"""Sonarr HTTP client (TV Series).

Extends :class:`BaseArrClient` with Sonarr-specific endpoints for series
management, episodes, episode files, and language profiles.
"""

from __future__ import annotations

from typing import Any

from arr_mcp.constants import DEFAULT_TIMEOUT, SONARR_API_PATH
from arr_mcp.services.base import BaseArrClient


class SonarrClient(BaseArrClient):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        super().__init__(
            name="Sonarr",
            base_url=base_url,
            api_key=api_key,
            api_path=SONARR_API_PATH,
            timeout=timeout,
        )

    # ── series ────────────────────────────────────────────────────

    async def get_series(self, tvdb_id: int | None = None) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if tvdb_id:
            params["tvdbId"] = tvdb_id
        return await self._get(f"{self.api_path}/series", **params)  # type: ignore[return-value]

    async def get_series_by_id(self, series_id: int) -> dict[str, Any]:
        return await self._get(f"{self.api_path}/series/{series_id}")  # type: ignore[return-value]

    async def lookup_series(self, term: str) -> list[dict[str, Any]]:
        return await self._get(f"{self.api_path}/series/lookup", term=term)  # type: ignore[return-value]

    async def add_series(
        self,
        tvdb_id: int,
        title: str,
        quality_profile_id: int,
        root_folder_path: str,
        monitored: bool = True,
        search_for_missing_episodes: bool = True,
        **kwargs: Any,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "tvdbId": tvdb_id,
            "title": title,
            "qualityProfileId": quality_profile_id,
            "rootFolderPath": root_folder_path,
            "monitored": monitored,
            "addOptions": {
                "searchForMissingEpisodes": search_for_missing_episodes,
            },
            **kwargs,
        }
        return await self._post(f"{self.api_path}/series", json=payload)

    async def delete_series(self, series_id: int, delete_files: bool = False) -> dict[str, Any]:
        return await self._delete(  # type: ignore[return-value]
            f"{self.api_path}/series/{series_id}",
            deleteFiles=delete_files,
        )

    async def update_series(self, series_id: int, **fields: Any) -> dict[str, Any]:
        series = await self.get_series_by_id(series_id)
        series.update(fields)
        return await self._put(f"{self.api_path}/series/{series_id}", json=series)

    # ── episodes ──────────────────────────────────────────────────

    async def get_episodes(
        self,
        series_id: int,
        season_number: int | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"seriesId": series_id}
        if season_number is not None:
            params["seasonNumber"] = season_number
        return await self._get(f"{self.api_path}/episode", **params)  # type: ignore[return-value]

    async def get_episode(self, episode_id: int) -> dict[str, Any]:
        return await self._get(f"{self.api_path}/episode/{episode_id}")  # type: ignore[return-value]

    async def update_episode(self, episode_id: int, **fields: Any) -> dict[str, Any]:
        episode = await self.get_episode(episode_id)
        episode.update(fields)
        return await self._put(f"{self.api_path}/episode/{episode_id}", json=episode)

    # ── episode files ─────────────────────────────────────────────

    async def get_episode_files(self, series_id: int | None = None) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if series_id:
            params["seriesId"] = series_id
        return await self._get(f"{self.api_path}/episodefile", **params)  # type: ignore[return-value]

    async def get_episode_file(self, file_id: int) -> dict[str, Any]:
        return await self._get(f"{self.api_path}/episodefile/{file_id}")  # type: ignore[return-value]

    async def delete_episode_file(self, file_id: int) -> dict[str, Any]:
        return await self._delete(f"{self.api_path}/episodefile/{file_id}")  # type: ignore[return-value]

    # ── language profiles ─────────────────────────────────────────

    async def get_language_profiles(self) -> list[dict[str, Any]]:
        return await self._get(f"{self.api_path}/languageprofile")  # type: ignore[return-value]
