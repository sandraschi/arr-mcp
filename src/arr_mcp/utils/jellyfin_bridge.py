"""Jellyfin HTTP bridge for cross-arr orchestration.

Queries Jellyfin to check if a media title already exists in the library before
routing a request to the appropriate *arr service.  Requires ``JELLYFIN_URL``
and ``JELLYFIN_API_KEY`` in ``.env``.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from arr_mcp.constants import DEFAULT_TIMEOUT, MEDIA_TYPE_TO_JELLYFIN_ITEM, MediaType

logger = logging.getLogger(__name__)


class JellyfinBridge:
    """Thin HTTP wrapper around Jellyfin's REST API for library look-ups."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    @property
    def is_configured(self) -> bool:
        return bool(self.base_url and self.api_key)

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={"X-MediaBrowser-Token": self.api_key},
                timeout=self.timeout,
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def search(
        self,
        term: str,
        media_types: list[MediaType] | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search the Jellyfin library for a title.

        Parameters
        ----------
        term:
            Search term (movie title, series name, album, book, etc.).
        media_types:
            Item types to include.  Defaults to Movie + Series.
        limit:
            Max results to return.
        """
        if not self.is_configured:
            logger.warning("Jellyfin not configured — skipping search")
            return []

        if media_types is None:
            media_types = [MediaType.MOVIE, MediaType.SERIES]

        include_types = ",".join(MEDIA_TYPE_TO_JELLYFIN_ITEM[mt] for mt in media_types)

        client = await self._ensure_client()
        resp = await client.get(
            "/Items",
            params={
                "searchTerm": term,
                "IncludeItemTypes": include_types,
                "Recursive": "true",
                "Limit": limit,
            },
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("Items", [])

    async def find_title(
        self,
        title: str,
        media_type: MediaType | None = None,
        year: int | None = None,
    ) -> dict[str, Any] | None:
        """Check if a specific title exists in Jellyfin.

        Returns the first matching item or ``None``.
        """
        types = [media_type] if media_type else [MediaType.MOVIE, MediaType.SERIES]
        items = await self.search(title, media_types=types)

        # filter by year if provided
        if year:
            items = [i for i in items if i.get("ProductionYear") == year]

        return items[0] if items else None

    async def check_availability(
        self,
        title: str,
        media_type: MediaType | None = None,
    ) -> dict[str, Any]:
        """Check if a title is available in Jellyfin.

        ## Return Format
        {
            "available": bool,
            "title": str,
            "matched_title": str | None,
            "media_type": str | None,
            "jellyfin_id": str | None,
            "in_library": bool,
        }
        """
        if not self.is_configured:
            return {
                "available": False,
                "title": title,
                "matched_title": None,
                "media_type": None,
                "jellyfin_id": None,
                "in_library": False,
                "note": "Jellyfin not configured",
            }

        item = await self.find_title(title, media_type=media_type)

        if item:
            return {
                "available": True,
                "title": title,
                "matched_title": item.get("Name"),
                "media_type": item.get("Type"),
                "jellyfin_id": item.get("Id"),
                "in_library": True,
            }

        return {
            "available": False,
            "title": title,
            "matched_title": None,
            "media_type": None,
            "jellyfin_id": None,
            "in_library": False,
        }
