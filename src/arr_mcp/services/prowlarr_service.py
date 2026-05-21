"""Prowlarr HTTP client (Indexer Backbone).

Prowlarr is the indexer backbone of the *arr stack. Unlike other *arr apps it
manages indexers (Usenet/Torrent) and syncs them to Radarr/Sonarr/etc.  Its
``/api/v1/search`` endpoint provides unified search across ALL configured
indexers with category filtering.
"""

from __future__ import annotations

from typing import Any

from arr_mcp.constants import DEFAULT_TIMEOUT, PROWLARR_API_PATH
from arr_mcp.services.base import BaseArrClient


class ProwlarrClient(BaseArrClient):
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        super().__init__(
            name="Prowlarr",
            base_url=base_url,
            api_key=api_key,
            api_path=PROWLARR_API_PATH,
            timeout=timeout,
        )

    # ── indexers ──────────────────────────────────────────────────

    async def get_indexers(self) -> list[dict[str, Any]]:
        return await self._get(f"{self.api_path}/indexer")  # type: ignore[return-value]

    async def get_indexer(self, indexer_id: int) -> dict[str, Any]:
        return await self._get(f"{self.api_path}/indexer/{indexer_id}")  # type: ignore[return-value]

    async def add_indexer(self, **fields: Any) -> dict[str, Any]:
        return await self._post(f"{self.api_path}/indexer", json=fields)

    async def update_indexer(self, indexer_id: int, **fields: Any) -> dict[str, Any]:
        return await self._put(f"{self.api_path}/indexer/{indexer_id}", json=fields)

    async def delete_indexer(self, indexer_id: int) -> dict[str, Any]:
        return await self._delete(f"{self.api_path}/indexer/{indexer_id}")  # type: ignore[return-value]

    async def test_indexer(self, indexer_id: int) -> dict[str, Any]:
        indexer = await self.get_indexer(indexer_id)
        return await self._post(f"{self.api_path}/indexer/test", json=indexer)

    async def test_all_indexers(self) -> dict[str, Any]:
        return await self._post(f"{self.api_path}/indexer/testall")

    async def get_indexer_schema(self) -> list[dict[str, Any]]:
        return await self._get(f"{self.api_path}/indexer/schema")  # type: ignore[return-value]

    # ── unified search ────────────────────────────────────────────

    async def search(
        self,
        query: str,
        categories: list[int] | None = None,
        indexer_ids: list[int] | None = None,
        search_type: str = "search",
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {
            "query": query,
            "type": search_type,
            "limit": limit,
            "offset": offset,
        }
        if categories:
            params["categories"] = categories
        if indexer_ids:
            params["indexerIds"] = indexer_ids
        return await self._get(f"{self.api_path}/search", **params)  # type: ignore[return-value]

    # ── applications (synced arr apps) ────────────────────────────

    async def get_applications(self) -> list[dict[str, Any]]:
        return await self._get(f"{self.api_path}/applications")  # type: ignore[return-value]

    async def get_application(self, app_id: int) -> dict[str, Any]:
        return await self._get(f"{self.api_path}/applications/{app_id}")  # type: ignore[return-value]

    async def sync_application(self, app_id: int) -> dict[str, Any]:
        """Sync indexers for a specific application (Radarr/Sonarr/Lidarr)."""
        return await self._post(f"{self.api_path}/applications/{app_id}/sync")

    async def sync_all_applications(self) -> dict[str, Any]:
        """Trigger full indexer sync across all connected applications."""
        return await self._post(f"{self.api_path}/applications/syncall")

    async def test_application(self, app_id: int) -> dict[str, Any]:
        app = await self.get_application(app_id)
        return await self._post(f"{self.api_path}/applications/test", json=app)

    # ── history ───────────────────────────────────────────────────

    async def get_history_since(self, date: str) -> list[dict[str, Any]]:
        return await self._get(f"{self.api_path}/history/since", date=date)  # type: ignore[return-value]

    async def get_indexer_history(self, indexer_id: int, limit: int = 50) -> list[dict[str, Any]]:
        return await self._get(  # type: ignore[return-value]
            f"{self.api_path}/history/indexer",
            indexerId=indexer_id,
            limit=limit,
        )

    # ── notifications ─────────────────────────────────────────────

    async def get_notifications(self) -> list[dict[str, Any]]:
        return await self._get(f"{self.api_path}/notification")  # type: ignore[return-value]

    # ── download clients ──────────────────────────────────────────

    async def get_download_clients(self) -> list[dict[str, Any]]:
        return await self._get(f"{self.api_path}/downloadclient")  # type: ignore[return-value]

    # ── stats ─────────────────────────────────────────────────────

    async def get_indexer_stats(self) -> dict[str, Any]:
        return await self._get(f"{self.api_path}/indexerstats")  # type: ignore[return-value]

    # ── notifications schema ──────────────────────────────────────

    async def get_notification_schema(self) -> list[dict[str, Any]]:
        return await self._get(f"{self.api_path}/notification/schema")  # type: ignore[return-value]
