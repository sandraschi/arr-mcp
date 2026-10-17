"""Cross-arr orchestration tools - the differentiator.

The ``arr_orchestrate`` tool is arr-mcp's unique value proposition:
given a media title, it checks Jellyfin for availability, auto-detects
the media type, and routes the request to the correct *arr service.

Additionally provides unified calendar and consolidated stats across the
entire stack.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import Annotated, Literal

from pydantic import Field

from arr_mcp.constants import TOOL_VERSION, ArrServiceName, MediaType, service_key
from arr_mcp.orchestration import build_bridges, request_media

logger = logging.getLogger(__name__)


def register_cross_arr_tools(mcp, clients: dict, config) -> None:
    """Register cross-arr orchestration tools.

    Parameters
    ----------
    clients:
        Dict mapping :class:`ArrServiceName` → client instance (or None).
    config:
        The full :class:`ArrConfig`.
    """
    bridges = build_bridges(config)

    @mcp.tool(
        annotations={"readOnlyHint": False, "destructiveHint": False},
        version=TOOL_VERSION,
    )
    async def arr_orchestrate(
        operation: Annotated[
            Literal["request", "status", "check_jellyfin", "check_plex", "check_emby", "queue"],
            Field(description="Operation: request a title, stack status, check Jellyfin/Plex/Emby, or show queue."),
        ],
        media_title: Annotated[str | None, Field(description="Media title for request / media server check.")] = None,
        media_type: Annotated[
            str | None,
            Field(description="Media type: 'movie', 'series', 'album', 'book'. Auto-detected if omitted."),
        ] = None,
        year: Annotated[int | None, Field(description="Year for disambiguation.")] = None,
        quality_profile_id: Annotated[int | None, Field(description="Quality profile ID for auto-add.")] = None,
        root_folder_path: Annotated[str | None, Field(description="Root folder path for auto-add.")] = None,
        media_server: Annotated[
            str | None,
            Field(
                description="Media server to check: 'jellyfin', 'plex', 'emby', or None for auto (check all configured)."
            ),
        ] = None,
    ) -> dict:
        """Cross-arr orchestration: check Jellyfin/Plex/Emby, auto-route to correct arr, stack status.

        **THE DIFFERENTIATOR** - chains media server availability checks
        (Jellyfin + Plex + Emby) with automatic *arr routing. "I want to watch Dune"
        → checks configured media servers → if not found → auto-adds to Radarr.

        ## Return Format
        {"success": bool, "message": str, "pipeline": [...], "data": {...}}

        ## Examples
        arr_orchestrate(operation="request", media_title="Dune")
        arr_orchestrate(operation="request", media_title="The Expanse", media_type="series")
        arr_orchestrate(operation="status")
        arr_orchestrate(operation="check_jellyfin", media_title="Inception")
        arr_orchestrate(operation="check_plex", media_title="Inception")
        arr_orchestrate(operation="check_emby", media_title="Inception")
        arr_orchestrate(operation="queue")
        """
        try:
            if operation == "status":
                return await _stack_status(clients)

            if operation == "queue":
                return await _stack_queue(clients)

            if operation == "check_jellyfin":
                if not media_title:
                    return {"success": False, "message": "media_title is required", "pipeline": [], "data": {}}
                mt = MediaType(media_type) if media_type else None
                result = await bridges["jellyfin"].check_availability(media_title, media_type=mt)
                return {
                    "success": True,
                    "message": f"{media_title} is {'IN' if result['in_library'] else 'NOT'} in Jellyfin",
                    "pipeline": ["jellyfin_check"],
                    "data": result,
                }

            if operation == "check_plex":
                if not media_title:
                    return {"success": False, "message": "media_title is required", "pipeline": [], "data": {}}
                mt = MediaType(media_type) if media_type else None
                result = await bridges["plex"].check_availability(media_title, media_type=mt)
                return {
                    "success": True,
                    "message": f"{media_title} is {'IN' if result['in_library'] else 'NOT'} in Plex",
                    "pipeline": ["plex_check"],
                    "data": result,
                }

            if operation == "check_emby":
                if not media_title:
                    return {"success": False, "message": "media_title is required", "pipeline": [], "data": {}}
                mt = MediaType(media_type) if media_type else None
                result = await bridges["emby"].check_availability(media_title, media_type=mt)
                return {
                    "success": True,
                    "message": f"{media_title} is {'IN' if result['in_library'] else 'NOT'} in Emby",
                    "pipeline": ["emby_check"],
                    "data": result,
                }

            if operation == "request":
                if not media_title:
                    return {"success": False, "message": "media_title is required", "pipeline": [], "data": {}}
                return await request_media(
                    clients,
                    bridges,
                    media_title,
                    media_type=media_type,
                    quality_profile_id=quality_profile_id,
                    root_folder_path=root_folder_path,
                    media_server=media_server,
                )

            return {"success": False, "message": f"Unknown operation: {operation}", "pipeline": [], "data": {}}

        except Exception as e:
            logger.exception("arr_orchestrate failed: %s", e)
            return {"success": False, "message": str(e), "pipeline": [], "data": {}}

    @mcp.tool(
        annotations={"readOnlyHint": True, "destructiveHint": False},
        version=TOOL_VERSION,
    )
    async def arr_calendar(
        operation: Annotated[
            Literal["upcoming", "today", "week", "range"],
            Field(description="Time range: upcoming (all future), today, this week, or custom range."),
        ],
        start: Annotated[str | None, Field(description="ISO datetime start for 'range'.")] = None,
        end: Annotated[str | None, Field(description="ISO datetime end for 'range'.")] = None,
        types: Annotated[
            list[str] | None, Field(description="Filter by media types: 'movie','series','album','book'.")
        ] = None,
    ) -> dict:
        """Unified calendar across Radarr, Sonarr, Lidarr, and Readarr.

        Aggregates upcoming releases from all configured *arr services into a
        single timeline.

        ## Return Format
        {"success": bool, "message": str, "data": {arr_name: [...]}}

        ## Examples
        arr_calendar(operation="upcoming")
        arr_calendar(operation="today")
        arr_calendar(operation="range", start="2026-06-01", end="2026-06-07")
        """
        try:
            now = datetime.now(UTC)
            if operation == "today":
                start_str = now.strftime("%Y-%m-%dT00:00:00Z")
                end_str = now.strftime("%Y-%m-%dT23:59:59Z")
            elif operation == "week":
                start_str = now.strftime("%Y-%m-%dT00:00:00Z")
                end_of_week = now + timedelta(days=6)
                end_str = end_of_week.strftime("%Y-%m-%dT23:59:59Z")
            elif operation == "range":
                start_str = start or now.strftime("%Y-%m-%dT00:00:00Z")
                end_str = end or now.strftime("%Y-%m-%dT23:59:59Z")
            else:
                start_str = now.strftime("%Y-%m-%dT00:00:00Z")
                end_str = (now + timedelta(days=30)).strftime("%Y-%m-%dT23:59:59Z")

            results: dict[str, list[dict]] = {}
            type_filter = [MediaType(t) for t in types] if types else None

            calendar_services = [
                ("radarr", clients.get(ArrServiceName.RADARR)),
                ("sonarr", clients.get(ArrServiceName.SONARR)),
                ("lidarr", clients.get(ArrServiceName.LIDARR)),
                ("readarr", clients.get(ArrServiceName.READARR)),
            ]

            for name, client in calendar_services:
                if client is None:
                    continue
                if type_filter and MediaType(name.rstrip("s")) not in type_filter and name != "sonarr":
                    continue
                try:
                    data = await client.get_calendar(start=start_str, end=end_str)
                    results[name] = data
                except Exception as exc:
                    logger.warning("Calendar fetch failed for %s: %s", name, exc)
                    results[name] = []

            total = sum(len(v) for v in results.values())
            return {
                "success": True,
                "message": f"Found {total} upcoming items across {len(results)} services",
                "data": results,
            }

        except Exception as e:
            logger.exception("arr_calendar failed: %s", e)
            return {"success": False, "message": str(e), "data": {}}

    @mcp.tool(
        annotations={"readOnlyHint": True, "destructiveHint": False},
        version=TOOL_VERSION,
    )
    async def arr_stats(
        operation: Annotated[
            Literal["summary", "disk", "queues", "history"],
            Field(description="Stats type: summary overview, disk usage, active queues, or recent history."),
        ],
    ) -> dict:
        """Consolidated statistics across the entire *arr stack.

        ## Return Format
        {"success": bool, "message": str, "data": {arr_name: {...}}}

        ## Examples
        arr_stats(operation="summary")
        arr_stats(operation="disk")
        arr_stats(operation="queues")
        """
        try:
            if operation == "summary":
                return await _stack_summary(clients)

            if operation == "disk":
                return await _stack_disk(clients)

            if operation == "queues":
                return await _stack_queue(clients)

            if operation == "history":
                return await _stack_history(clients)

            return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            logger.exception("arr_stats failed: %s", e)
            return {"success": False, "message": str(e), "data": {}}


# ── internal helpers ──────────────────────────────────────────────
# Request-pipeline helpers (detect_media_type, check_already_queued,
# add_to_arr) live in arr_mcp.orchestration and are imported above under
# their historic underscore aliases so existing imports keep working.


async def _stack_status(clients: dict) -> dict:
    """Get system status for all configured arrs."""
    result: dict[str, dict] = {}
    for name, client in clients.items():
        if client is None:
            result[service_key(name)] = {"reachable": False, "reason": "not configured"}
            continue
        try:
            status = await client.get_system_status()
            result[service_key(name)] = {
                "reachable": True,
                "version": status.get("version"),
                "status": status,
            }
        except Exception as e:
            result[service_key(name)] = {"reachable": False, "reason": str(e)}

    reachable = sum(1 for v in result.values() if v.get("reachable"))
    total = len(result)
    return {"success": True, "message": f"{reachable}/{total} services reachable", "data": result}


async def _stack_summary(clients: dict) -> dict:
    """Get a high-level summary across the stack."""
    result: dict[str, dict] = {}
    total_items = 0
    total_wanted = 0

    summary_targets = [
        (ArrServiceName.RADARR, "get_movies", "movies"),
        (ArrServiceName.SONARR, "get_series", "series"),
        (ArrServiceName.LIDARR, "get_artists", "artists"),
        (ArrServiceName.READARR, "get_authors", "authors"),
    ]

    for arr_name, method_name, label in summary_targets:
        client = clients.get(arr_name)
        if client is None:
            result[service_key(arr_name)] = {"enabled": False, label: 0, "wanted": 0}
            continue
        try:
            method = getattr(client, method_name)
            items = await method()
            wanted = await client.get_wanted_missing()
            count = len(items)
            wanted_count = wanted.get("totalRecords", len(wanted.get("records", [])))
            total_items += count
            total_wanted += wanted_count
            result[service_key(arr_name)] = {"enabled": True, label: count, "wanted": wanted_count}
        except Exception as e:
            result[service_key(arr_name)] = {"enabled": True, label: 0, "wanted": 0, "error": str(e)}

    return {
        "success": True,
        "message": f"Stack: {total_items} total items, {total_wanted} wanted/missing",
        "data": result,
    }


async def _stack_disk(clients: dict) -> dict:
    """Get disk space across all arrs."""
    result: dict[str, dict] = {}
    for name, client in clients.items():
        if client is None:
            continue
        try:
            disks = await client.get_diskspace()
            result[service_key(name)] = disks
        except Exception as e:
            result[service_key(name)] = [{"error": str(e)}]

    return {"success": True, "message": f"Disk info for {len(result)} services", "data": result}


async def _stack_queue(clients: dict) -> dict:
    """Get active download queues."""
    result: dict[str, dict] = {}
    total = 0
    for name, client in clients.items():
        if client is None:
            continue
        try:
            queue = await client.get_queue()
            count = queue.get("totalRecords", len(queue.get("records", [])))
            total += count
            result[service_key(name)] = queue
        except Exception as e:
            result[service_key(name)] = {"error": str(e)}

    return {"success": True, "message": f"{total} active downloads across {len(result)} services", "data": result}


async def _stack_history(clients: dict) -> dict:
    """Get recent history across all arrs."""
    result: dict[str, dict] = {}
    for name, client in clients.items():
        if client is None:
            continue
        try:
            history = await client.get_history(page_size=10)
            result[service_key(name)] = history
        except Exception as e:
            result[service_key(name)] = {"error": str(e)}

    return {"success": True, "message": f"Recent history for {len(result)} services", "data": result}
