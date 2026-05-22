"""Shared base HTTP client for all Servarr-based *arr services.

Radarr, Sonarr, Lidarr, Prowlarr, and Readarr share ~60% of their API surface
deriving from the common Servarr codebase.  This base client implements all
shared endpoints; per-arr service sub-classes add domain-specific methods.
"""

import logging
from typing import Any

import httpx

from arr_mcp.constants import DEFAULT_TIMEOUT

logger = logging.getLogger(__name__)


class BaseArrClient:
    """Shared httpx AsyncClient for *arr REST APIs.

    All Servarr-based apps expose the same authentication model (``X-Api-Key``
    header), pagination pattern, health endpoint, queue, history, wanted, calendar,
    command system, tags, logs, blocklist, and system status.

    Parameters
    ----------
    name:
        Human-readable service name used in log messages.
    base_url:
        Root URL of the *arr instance (e.g. ``http://localhost:7878``).
    api_key:
        API key from the *arr web UI (Settings → General).
    api_path:
        Versioned API prefix (e.g. ``/api/v3`` for Radarr/Sonarr, ``/api/v1`` for
        Lidarr/Prowlarr/Readarr).
    timeout:
        HTTP request timeout in seconds.
    """

    def __init__(
        self,
        name: str,
        base_url: str,
        api_key: str,
        api_path: str,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self.name = name
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.api_path = api_path
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

    # ── internal helpers ──────────────────────────────────────────

    async def _get(self, path: str, **params: Any) -> dict[str, Any] | list[dict[str, Any]]:
        client = await self._ensure_client()
        resp = await client.get(path, params=params)
        resp.raise_for_status()
        return resp.json()

    async def _post(self, path: str, json: dict[str, Any] | None = None, **params: Any) -> dict[str, Any]:
        client = await self._ensure_client()
        resp = await client.post(path, json=json, params=params)
        resp.raise_for_status()
        return resp.json()

    async def _put(self, path: str, json: dict[str, Any] | None = None, **params: Any) -> dict[str, Any]:
        client = await self._ensure_client()
        resp = await client.put(path, json=json, params=params)
        resp.raise_for_status()
        return resp.json()

    async def _delete(self, path: str, json: dict[str, Any] | None = None, **params: Any) -> dict[str, Any]:
        client = await self._ensure_client()
        if json is not None:
            resp = await client.request("DELETE", path, params=params, json=json)
        else:
            resp = await client.delete(path, params=params)
        resp.raise_for_status()
        return resp.json()

    # ── API info ──────────────────────────────────────────────────

    async def get_api_info(self) -> dict[str, Any]:
        return await self._get("/api")  # type: ignore[return-value]

    # ── system status ─────────────────────────────────────────────

    async def get_system_status(self) -> dict[str, Any]:
        return await self._get(f"{self.api_path}/system/status")  # type: ignore[return-value]

    async def health_check(self) -> dict[str, Any]:
        """Return system status as a simple health probe (alias)."""
        return await self.get_system_status()

    # ── disk space ────────────────────────────────────────────────

    async def get_diskspace(self) -> list[dict[str, Any]]:
        return await self._get(f"{self.api_path}/diskspace")  # type: ignore[return-value]

    # ── queue ─────────────────────────────────────────────────────

    async def get_queue(
        self,
        page: int = 1,
        page_size: int = 20,
        include_unknown: bool = True,
    ) -> dict[str, Any]:
        return await self._get(  # type: ignore[return-value]
            f"{self.api_path}/queue",
            page=page,
            pageSize=page_size,
            includeUnknownMovieItems=include_unknown,
        )

    # ── history ───────────────────────────────────────────────────

    async def get_history(
        self,
        page: int = 1,
        page_size: int = 20,
        sort_key: str = "date",
        sort_direction: str = "descending",
    ) -> dict[str, Any]:
        return await self._get(  # type: ignore[return-value]
            f"{self.api_path}/history",
            page=page,
            pageSize=page_size,
            sortKey=sort_key,
            sortDirection=sort_direction,
        )

    # ── wanted / missing ──────────────────────────────────────────

    async def get_wanted_missing(
        self,
        page: int = 1,
        page_size: int = 20,
        sort_key: str = "title",
        sort_direction: str = "ascending",
        monitored: bool = True,
    ) -> dict[str, Any]:
        return await self._get(  # type: ignore[return-value]
            f"{self.api_path}/wanted/missing",
            page=page,
            pageSize=page_size,
            sortKey=sort_key,
            sortDirection=sort_direction,
            monitored=monitored,
        )

    # ── calendar ──────────────────────────────────────────────────

    async def get_calendar(
        self,
        start: str | None = None,
        end: str | None = None,
        unmonitored: bool = False,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"unmonitored": unmonitored}
        if start:
            params["start"] = start
        if end:
            params["end"] = end
        return await self._get(f"{self.api_path}/calendar", **params)  # type: ignore[return-value]

    # ── commands ──────────────────────────────────────────────────

    async def get_commands(self) -> list[dict[str, Any]]:
        return await self._get(f"{self.api_path}/command")  # type: ignore[return-value]

    async def trigger_command(self, name: str, **body: Any) -> dict[str, Any]:
        payload: dict[str, Any] = {"name": name, **body}
        return await self._post(f"{self.api_path}/command", json=payload)

    # ── tags ──────────────────────────────────────────────────────

    async def get_tags(self) -> list[dict[str, Any]]:
        return await self._get(f"{self.api_path}/tag")  # type: ignore[return-value]

    # ── logs ──────────────────────────────────────────────────────

    async def get_logs(
        self,
        page: int = 1,
        page_size: int = 50,
        sort_key: str = "time",
        sort_direction: str = "descending",
    ) -> dict[str, Any]:
        return await self._get(  # type: ignore[return-value]
            f"{self.api_path}/log",
            page=page,
            pageSize=page_size,
            sortKey=sort_key,
            sortDirection=sort_direction,
        )

    # ── blocklist ─────────────────────────────────────────────────

    async def get_blocklist(
        self,
        page: int = 1,
        page_size: int = 20,
        sort_key: str = "date",
        sort_direction: str = "descending",
    ) -> dict[str, Any]:
        return await self._get(  # type: ignore[return-value]
            f"{self.api_path}/blocklist",
            page=page,
            pageSize=page_size,
            sortKey=sort_key,
            sortDirection=sort_direction,
        )

    async def delete_blocklist_item(self, item_id: int) -> dict[str, Any]:
        return await self._delete(f"{self.api_path}/blocklist/{item_id}")  # type: ignore[return-value]

    async def delete_blocklist_bulk(self, ids: list[int]) -> dict[str, Any]:
        return await self._delete(  # type: ignore[return-value]
            f"{self.api_path}/blocklist/bulk",
            json={"ids": ids},
        )

    # ── quality profiles ──────────────────────────────────────────

    async def get_quality_profiles(self) -> list[dict[str, Any]]:
        return await self._get(f"{self.api_path}/qualityprofile")  # type: ignore[return-value]

    # ── root folders ──────────────────────────────────────────────

    async def get_root_folders(self) -> list[dict[str, Any]]:
        return await self._get(f"{self.api_path}/rootfolder")  # type: ignore[return-value]

    # ── custom formats ────────────────────────────────────────────

    async def get_custom_formats(self) -> list[dict[str, Any]]:
        return await self._get(f"{self.api_path}/customformat")  # type: ignore[return-value]
