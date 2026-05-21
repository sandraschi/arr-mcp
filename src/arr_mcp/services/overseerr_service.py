"""Overseerr HTTP client (Media Requests & Discovery).

Overseerr is a request management and media discovery tool that integrates
with Radarr and Sonarr. It provides a user-friendly UI for requesting movies
and TV shows, auto-approval rules, and issue reporting.

Default port: 5055
Auth: X-Api-Key header
"""

from __future__ import annotations

from typing import Any

import httpx

from arr_mcp.constants import DEFAULT_TIMEOUT


class OverseerrClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self.name = "Overseerr"
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

    async def _post(self, path: str, json: dict[str, Any] | None = None, **params: Any) -> Any:
        client = await self._ensure_client()
        resp = await client.post(path, json=json, params=params)
        resp.raise_for_status()
        return resp.json()

    async def _put(self, path: str, json: dict[str, Any] | None = None, **params: Any) -> Any:
        client = await self._ensure_client()
        resp = await client.put(path, json=json, params=params)
        resp.raise_for_status()
        return resp.json()

    async def _delete(self, path: str, **params: Any) -> Any:
        client = await self._ensure_client()
        resp = await client.delete(path, params=params)
        resp.raise_for_status()
        return resp.json()

    # ── status ────────────────────────────────────────────────────

    async def get_status(self) -> dict[str, Any]:
        return await self._get("/api/v1/status")  # type: ignore[return-value]

    async def get_status_appdata(self) -> dict[str, Any]:
        return await self._get("/api/v1/status/appdata")  # type: ignore[return-value]

    async def health_check(self) -> dict[str, Any]:
        return await self.get_status()

    # ── search ────────────────────────────────────────────────────

    async def search(self, query: str, page: int = 1) -> dict[str, Any]:
        return await self._get("/api/v1/search", query=query, page=page)  # type: ignore[return-value]

    # ── requests ──────────────────────────────────────────────────

    async def get_requests(
        self,
        take: int = 20,
        skip: int = 0,
        request_filter: str = "all",
        sort: str = "added",
    ) -> dict[str, Any]:
        return await self._get(  # type: ignore[return-value]
            "/api/v1/request",
            take=take,
            skip=skip,
            request_filter=request_filter,
            sort=sort,
        )

    async def get_request(self, request_id: int) -> dict[str, Any]:
        return await self._get(f"/api/v1/request/{request_id}")  # type: ignore[return-value]

    async def create_request(
        self,
        media_type: str,
        media_id: int,
        tvdb_id: int | None = None,
        seasons: list[int] | None = None,
        is4k: bool = False,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "mediaType": media_type,
            "mediaId": media_id,
            "is4k": is4k,
        }
        if tvdb_id:
            payload["tvdbId"] = tvdb_id
        if seasons:
            payload["seasons"] = seasons
        return await self._post("/api/v1/request", json=payload)

    async def approve_request(self, request_id: int) -> dict[str, Any]:
        return await self._post(f"/api/v1/request/{request_id}/approve")

    async def decline_request(self, request_id: int) -> dict[str, Any]:
        return await self._post(f"/api/v1/request/{request_id}/decline")

    async def delete_request(self, request_id: int) -> dict[str, Any]:
        return await self._delete(f"/api/v1/request/{request_id}")  # type: ignore[return-value]

    # ── request count ─────────────────────────────────────────────

    async def get_request_count(self) -> dict[str, Any]:
        return await self._get("/api/v1/request/count")  # type: ignore[return-value]

    # ── users ─────────────────────────────────────────────────────

    async def get_users(self, take: int = 20, skip: int = 0) -> dict[str, Any]:
        return await self._get("/api/v1/user", take=take, skip=skip)  # type: ignore[return-value]

    async def get_user(self, user_id: int) -> dict[str, Any]:
        return await self._get(f"/api/v1/user/{user_id}")  # type: ignore[return-value]

    async def get_user_requests(self, user_id: int, take: int = 20, skip: int = 0) -> dict[str, Any]:
        return await self._get(f"/api/v1/user/{user_id}/requests", take=take, skip=skip)  # type: ignore[return-value]

    # ── media ─────────────────────────────────────────────────────

    async def get_media(self, media_id: int) -> dict[str, Any]:
        return await self._get(f"/api/v1/media/{media_id}")  # type: ignore[return-value]

    # ── service (Radarr/Sonarr config) ────────────────────────────

    async def get_service_radarr(self) -> list[dict[str, Any]]:
        return await self._get("/api/v1/service/radarr")  # type: ignore[return-value]

    async def get_service_sonarr(self) -> list[dict[str, Any]]:
        return await self._get("/api/v1/service/sonarr")  # type: ignore[return-value]

    # ── issues ────────────────────────────────────────────────────

    async def get_issues(self, take: int = 20, skip: int = 0) -> dict[str, Any]:
        return await self._get("/api/v1/issue", take=take, skip=skip)  # type: ignore[return-value]

    async def get_issue(self, issue_id: int) -> dict[str, Any]:
        return await self._get(f"/api/v1/issue/{issue_id}")  # type: ignore[return-value]

    # ── notifications ─────────────────────────────────────────────

    async def get_notifications(self, take: int = 20, skip: int = 0) -> dict[str, Any]:
        return await self._get("/api/v1/notification", take=take, skip=skip)  # type: ignore[return-value]

    # ── settings ──────────────────────────────────────────────────

    async def get_settings_main(self) -> dict[str, Any]:
        return await self._get("/api/v1/settings/main")  # type: ignore[return-value]

    async def get_settings_plex(self) -> dict[str, Any]:
        return await self._get("/api/v1/settings/plex")  # type: ignore[return-value]

    async def get_settings_jellyfin(self) -> dict[str, Any]:
        return await self._get("/api/v1/settings/jellyfin")  # type: ignore[return-value]
