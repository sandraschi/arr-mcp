"""REST API router — exposes per-service data for the webapp dashboard.

Each endpoint queries the corresponding *arr service client and returns
live summary data (counts, health, queue, disk, wanted).
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


def create_api_router(clients: dict, log_buffer: list[dict] | None = None) -> APIRouter:
    router = APIRouter(prefix="/api")

    # ── health check (all services) ──────────────────────────────

    @router.get("/health")
    async def api_health():
        result: dict[str, dict] = {}
        for name, client in clients.items():
            if client is None:
                result[name] = {"reachable": False, "reason": "not configured"}
                continue
            try:
                status = await client.health_check()
                result[name] = {"reachable": True, "version": status.get("version")}
            except Exception as e:
                result[name] = {"reachable": False, "reason": str(e)}
        return JSONResponse(content={"success": True, "data": result})

    # ── logs ─────────────────────────────────────────────────────

    @router.get("/logs")
    async def api_logs(limit: int = 100):
        if log_buffer is None:
            return JSONResponse(content={"success": True, "data": []})
        entries = list(log_buffer)[-limit:]
        return JSONResponse(content={"success": True, "data": entries})

    # ── radarr ───────────────────────────────────────────────────

    @router.get("/radarr/summary")
    async def radarr_summary():
        client = clients.get("radarr")
        if client is None:
            raise HTTPException(404, "Radarr not configured")
        try:
            movies = await client.get_movies()
            wanted = await client.get_wanted_missing()
            queue = await client.get_queue()
            disk = await client.get_diskspace()
            return {
                "success": True,
                "data": {
                    "movies": len(movies),
                    "wanted": wanted.get("totalRecords", len(wanted.get("records", []))),
                    "queue": queue.get("totalRecords", len(queue.get("records", []))),
                    "disk": disk,
                },
            }
        except Exception as e:
            raise HTTPException(502, str(e)) from e

    @router.get("/radarr/movies")
    async def radarr_movies(limit: int = 50):
        client = clients.get("radarr")
        if client is None:
            raise HTTPException(404, "Radarr not configured")
        try:
            movies = await client.get_movies()
            return {"success": True, "data": movies[:limit]}
        except Exception as e:
            raise HTTPException(502, str(e)) from e

    # ── sonarr ───────────────────────────────────────────────────

    @router.get("/sonarr/summary")
    async def sonarr_summary():
        client = clients.get("sonarr")
        if client is None:
            raise HTTPException(404, "Sonarr not configured")
        try:
            series_list = await client.get_series()
            wanted = await client.get_wanted_missing()
            queue = await client.get_queue()
            disk = await client.get_diskspace()
            return {
                "success": True,
                "data": {
                    "series": len(series_list),
                    "wanted": wanted.get("totalRecords", len(wanted.get("records", []))),
                    "queue": queue.get("totalRecords", len(queue.get("records", []))),
                    "disk": disk,
                },
            }
        except Exception as e:
            raise HTTPException(502, str(e)) from e

    @router.get("/sonarr/series")
    async def sonarr_series(limit: int = 50):
        client = clients.get("sonarr")
        if client is None:
            raise HTTPException(404, "Sonarr not configured")
        try:
            series_list = await client.get_series()
            return {"success": True, "data": series_list[:limit]}
        except Exception as e:
            raise HTTPException(502, str(e)) from e

    # ── lidarr ───────────────────────────────────────────────────

    @router.get("/lidarr/summary")
    async def lidarr_summary():
        client = clients.get("lidarr")
        if client is None:
            raise HTTPException(404, "Lidarr not configured")
        try:
            artists = await client.get_artists()
            wanted = await client.get_wanted_missing()
            queue = await client.get_queue()
            disk = await client.get_diskspace()
            return {
                "success": True,
                "data": {
                    "artists": len(artists),
                    "wanted": wanted.get("totalRecords", len(wanted.get("records", []))),
                    "queue": queue.get("totalRecords", len(queue.get("records", []))),
                    "disk": disk,
                },
            }
        except Exception as e:
            raise HTTPException(502, str(e)) from e

    # ── prowlarr ─────────────────────────────────────────────────

    @router.get("/prowlarr/summary")
    async def prowlarr_summary():
        client = clients.get("prowlarr")
        if client is None:
            raise HTTPException(404, "Prowlarr not configured")
        try:
            indexers = await client.get_indexers()
            apps = await client.get_applications()
            stats = await client.get_indexer_stats()
            return {
                "success": True,
                "data": {
                    "indexers": len(indexers),
                    "applications": len(apps),
                    "stats": stats,
                },
            }
        except Exception as e:
            raise HTTPException(502, str(e)) from e

    # ── readarr ──────────────────────────────────────────────────

    @router.get("/readarr/summary")
    async def readarr_summary():
        client = clients.get("readarr")
        if client is None:
            raise HTTPException(404, "Readarr not configured")
        try:
            authors = await client.get_authors()
            wanted = await client.get_wanted_missing()
            queue = await client.get_queue()
            disk = await client.get_diskspace()
            return {
                "success": True,
                "data": {
                    "authors": len(authors),
                    "wanted": wanted.get("totalRecords", len(wanted.get("records", []))),
                    "queue": queue.get("totalRecords", len(queue.get("records", []))),
                    "disk": disk,
                },
            }
        except Exception as e:
            raise HTTPException(502, str(e)) from e

    # ── overseerr ────────────────────────────────────────────────

    @router.get("/overseerr/summary")
    async def overseerr_summary():
        client = clients.get("overseerr")
        if client is None:
            raise HTTPException(404, "Overseerr not configured")
        try:
            requests = await client.get_requests(take=1)
            pending = await client.get_requests(take=100, request_filter="pending")
            count = await client.get_request_count()
            return {
                "success": True,
                "data": {
                    "total_requests": requests.get("pageInfo", {}).get("total", 0),
                    "pending": len(pending.get("results", [])),
                    "counts": count,
                },
            }
        except Exception as e:
            raise HTTPException(502, str(e)) from e

    # ── bazarr ───────────────────────────────────────────────────

    @router.get("/bazarr/summary")
    async def bazarr_summary():
        client = clients.get("bazarr")
        if client is None:
            raise HTTPException(404, "Bazarr not configured")
        try:
            wanted = await client.get_all_wanted()
            movies_wanted = len(wanted.get("movies", {}).get("data", []))
            episodes_wanted = len(wanted.get("episodes", {}).get("data", []))
            providers = await client.get_providers()
            return {
                "success": True,
                "data": {
                    "movies_wanted": movies_wanted,
                    "episodes_wanted": episodes_wanted,
                    "total_wanted": movies_wanted + episodes_wanted,
                    "providers": len(providers),
                },
            }
        except Exception as e:
            raise HTTPException(502, str(e)) from e

    # ── orchestrator summary ─────────────────────────────────────

    @router.get("/orchestrator/summary")
    async def orchestrator_summary():
        result: dict[str, dict] = {}
        total_wanted = 0

        summary_targets = [
            ("radarr", "movies", "get_movies", "get_wanted_missing"),
            ("sonarr", "series", "get_series", "get_wanted_missing"),
            ("lidarr", "artists", "get_artists", "get_wanted_missing"),
            ("readarr", "authors", "get_authors", "get_wanted_missing"),
        ]

        for name, label, list_method, wanted_method in summary_targets:
            client = clients.get(name)
            if client is None:
                result[name] = {"enabled": False, label: 0, "wanted": 0}
                continue
            try:
                items = await getattr(client, list_method)()
                wanted = await getattr(client, wanted_method)()
                count = len(items)
                wanted_count = wanted.get("totalRecords", len(wanted.get("records", [])))
                total_wanted += wanted_count
                result[name] = {"enabled": True, label: count, "wanted": wanted_count}
            except Exception as e:
                result[name] = {"enabled": True, label: 0, "wanted": 0, "error": str(e)}

        return {
            "success": True,
            "data": result,
            "total_wanted": total_wanted,
        }

    return router
