"""Plex HTTP bridge for cross-arr orchestration.

Queries Plex Media Server to check if a media title already exists before
routing a request to the appropriate *arr service.  Requires ``PLEX_URL``
and ``PLEX_TOKEN`` in ``.env``.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from arr_mcp.constants import DEFAULT_TIMEOUT, MediaType, is_placeholder_credential

logger = logging.getLogger(__name__)

# Maps MediaType to Plex JSON API type strings
MEDIA_TYPE_TO_PLEX_TYPE: dict[MediaType, str] = {
    MediaType.MOVIE: "movie",
    MediaType.SERIES: "show",
    MediaType.ALBUM: "album",
}


class PlexBridge:
    """Thin HTTP wrapper around Plex Media Server REST API for library lookups."""

    def __init__(
        self,
        base_url: str,
        token: str,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    @property
    def is_configured(self) -> bool:
        # Placeholder tokens from .env.example count as UNCONFIGURED — see issue #1.
        return bool(self.base_url and self.token) and not is_placeholder_credential(self.token)

    async def _ensure_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "X-Plex-Token": self.token,
                    "Accept": "application/json",
                },
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
        """Search Plex libraries for a title."""
        if not self.is_configured:
            logger.warning("Plex not configured - skipping search")
            return []

        client = await self._ensure_client()
        resp = await client.get("/search", params={"query": term, "limit": limit})
        resp.raise_for_status()
        data = resp.json()

        items: list[dict[str, Any]] = []
        container = data.get("MediaContainer", {})
        for key in ("Video", "Directory"):
            items.extend(container.get(key, []))

        if media_types:
            type_ids = {MEDIA_TYPE_TO_PLEX_TYPE[mt] for mt in media_types if mt in MEDIA_TYPE_TO_PLEX_TYPE}
            items = [i for i in items if i.get("type") in type_ids]

        return items[:limit]

    async def find_title(
        self,
        title: str,
        media_type: MediaType | None = None,
        year: int | None = None,
    ) -> dict[str, Any] | None:
        """Check if a specific title exists in Plex.

        Returns the first matching item or ``None``.
        """
        types = [media_type] if media_type else [MediaType.MOVIE, MediaType.SERIES]
        items = await self.search(title, media_types=types)

        if year:
            items = [i for i in items if i.get("year") == year]

        return items[0] if items else None

    async def check_availability(
        self,
        title: str,
        media_type: MediaType | None = None,
    ) -> dict[str, Any]:
        """Check if a title is available in Plex.

        ## Return Format
        {
            "available": bool,
            "title": str,
            "matched_title": str | None,
            "media_type": str | None,
            "plex_rating_key": str | None,
            "in_library": bool,
        }
        """
        if not self.is_configured:
            return {
                "available": False,
                "title": title,
                "matched_title": None,
                "media_type": None,
                "plex_rating_key": None,
                "in_library": False,
                "note": "Plex not configured",
            }

        item = await self.find_title(title, media_type=media_type)

        if item:
            return {
                "available": True,
                "title": title,
                "matched_title": item.get("title"),
                "media_type": item.get("type"),
                "plex_rating_key": item.get("ratingKey"),
                "in_library": True,
            }

        return {
            "available": False,
            "title": title,
            "matched_title": None,
            "media_type": None,
            "plex_rating_key": None,
            "in_library": False,
        }
