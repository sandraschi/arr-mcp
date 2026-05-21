"""Bazarr HTTP client (Subtitles).

Bazarr is NOT Servarr-based — it is a standalone Python application with its
own REST API on port 6767.  This client implements direct HTTP calls to the
Bazarr API endpoints.

Unlike other arr services in this package, BazarrClient does NOT extend
BaseArrClient because the API surface is fundamentally different (no pagination
in the same style, different auth pattern options, etc.).
"""

from __future__ import annotations

from typing import Any

import httpx

from arr_mcp.constants import DEFAULT_TIMEOUT


class BazarrClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self.name = "Bazarr"
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"X-Api-Key": self.api_key},
                timeout=self.timeout,
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def _get(self, path: str, **params: Any) -> Any:
        client = await self._ensure_client()
        resp = await client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    async def _post(self, path: str, **params: Any) -> Any:
        client = await self._ensure_client()
        resp = await client.post(path, params=params)
        resp.raise_for_status()
        return resp.json()

    # ── system ────────────────────────────────────────────────────

    async def get_system_status(self) -> dict[str, Any]:
        return await self._get("/api/system/status")  # type: ignore[return-value]

    async def health_check(self) -> dict[str, Any]:
        return await self.get_system_status()

    # ── movies ────────────────────────────────────────────────────

    async def get_movies(self) -> list[dict[str, Any]]:
        return await self._get("/api/movies")  # type: ignore[return-value]

    # ── series / episodes ─────────────────────────────────────────

    async def get_series(self) -> list[dict[str, Any]]:
        return await self._get("/api/series")  # type: ignore[return-value]

    async def get_episodes(self, series_id: int) -> list[dict[str, Any]]:
        return await self._get("/api/episodes", seriesid=series_id)  # type: ignore[return-value]

    # ── wanted (missing subtitles) ────────────────────────────────

    async def get_wanted_movies(self) -> dict[str, Any]:
        return await self._get("/api/movies/wanted")  # type: ignore[return-value]

    async def get_wanted_episodes(self) -> dict[str, Any]:
        return await self._get("/api/episodes/wanted")  # type: ignore[return-value]

    async def get_all_wanted(self) -> dict[str, Any]:
        """Get all movies and episodes with missing subtitles."""
        movies = await self.get_wanted_movies()
        episodes = await self.get_wanted_episodes()
        return {"movies": movies, "episodes": episodes}

    # ── subtitles ─────────────────────────────────────────────────

    async def search_subtitles(
        self,
        episode_id: int | None = None,
        movie_id: int | None = None,
        language: str | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if episode_id:
            params["episodeid"] = episode_id
        if movie_id:
            params["movieid"] = movie_id
        if language:
            params["language"] = language
        return await self._get("/api/subtitles", **params)  # type: ignore[return-value]

    async def download_subtitle(
        self,
        subtitle_path: str,
        episode_id: int | None = None,
        movie_id: int | None = None,
        language: str | None = None,
        provider: str | None = None,
        scene_name: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {
            "subtitle": subtitle_path,
        }
        if episode_id:
            params["episodeid"] = episode_id
        if movie_id:
            params["movieid"] = movie_id
        if language:
            params["language"] = language
        if provider:
            params["provider"] = provider
        if scene_name:
            params["scenename"] = scene_name
        return await self._post("/api/subtitles", **params)  # type: ignore[return-value]

    # ── history ───────────────────────────────────────────────────

    async def get_history(self) -> list[dict[str, Any]]:
        return await self._get("/api/history")  # type: ignore[return-value]

    # ── providers ─────────────────────────────────────────────────

    async def get_providers(self) -> list[dict[str, Any]]:
        return await self._get("/api/providers")  # type: ignore[return-value]

    # ── languages ─────────────────────────────────────────────────

    async def get_languages(self) -> list[dict[str, Any]]:
        return await self._get("/api/languages")  # type: ignore[return-value]
