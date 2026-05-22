"""Shared test fixtures for MCP tool registration."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


class MockMCP:
    """Minimal FastMCP stand-in that captures registered tools."""

    def __init__(self) -> None:
        self.tools: dict[str, Callable[..., Any]] = {}

    def tool(self, **kwargs: Any):
        def decorator(fn: Callable[..., Any]):
            self.tools[fn.__name__] = fn
            return fn

        return decorator


class MockArrClient:
    """Configurable async client stub for stack/orchestration tests."""

    def __init__(
        self,
        *,
        version: str = "5.0.0",
        movies: list[dict] | None = None,
        wanted_records: list[dict] | None = None,
        queue_records: list[dict] | None = None,
        disk: list[dict] | None = None,
        history_records: list[dict] | None = None,
        lookup_movie_results: list[dict] | None = None,
        add_movie_result: dict | None = None,
    ) -> None:
        self.version = version
        self.movies = movies or []
        self.wanted_records = wanted_records or []
        self.queue_records = queue_records or []
        self.disk = disk or [{"path": "/data", "freeSpace": 1000}]
        self.history_records = history_records or []
        self.lookup_movie_results = lookup_movie_results or []
        self.add_movie_result = add_movie_result or {"id": 1, "title": "Dune"}

    async def get_system_status(self) -> dict:
        return {"version": self.version, "startupPath": "/app", "appData": "/config"}

    async def health_check(self) -> dict:
        return await self.get_system_status()

    async def get_movies(self) -> list[dict]:
        return self.movies

    async def get_series(self) -> list[dict]:
        return []

    async def get_artists(self) -> list[dict]:
        return []

    async def get_authors(self) -> list[dict]:
        return []

    async def get_wanted_missing(self) -> dict:
        return {"records": self.wanted_records, "totalRecords": len(self.wanted_records)}

    async def get_queue(self) -> dict:
        return {"records": self.queue_records, "totalRecords": len(self.queue_records)}

    async def get_diskspace(self) -> list[dict]:
        return self.disk

    async def get_history(self, page_size: int = 10) -> dict:
        return {"records": self.history_records[:page_size], "totalRecords": len(self.history_records)}

    async def get_calendar(self, start: str | None = None, end: str | None = None) -> list[dict]:
        return [{"title": "Upcoming", "date": start or "2026-06-01"}]

    async def lookup_movie(self, term: str) -> list[dict]:
        return self.lookup_movie_results

    async def add_movie(self, **kwargs) -> dict:
        return self.add_movie_result

    async def get_quality_profiles(self) -> list[dict]:
        return [{"id": 1, "name": "HD-1080p"}]

    async def get_root_folders(self) -> list[dict]:
        return [{"id": 1, "path": "/movies"}]

    async def lookup_series(self, term: str) -> list[dict]:
        return []

    async def lookup_artist(self, term: str) -> list[dict]:
        return []

    async def lookup_author(self, term: str) -> list[dict]:
        return []

    async def add_series(self, **kwargs) -> dict:
        return {"id": 1}

    async def add_artist(self, **kwargs) -> dict:
        return {"id": 1}

    async def add_author(self, **kwargs) -> dict:
        return {"id": 1}
