"""Cross-arr orchestration tools — the differentiator.

The ``arr_orchestrate`` tool is arr-mcp's unique value proposition:
given a media title, it checks Jellyfin for availability, auto-detects
the media type, and routes the request to the correct *arr service.

Additionally provides unified calendar and consolidated stats across the
entire stack.
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Annotated, Literal

from pydantic import Field

from arr_mcp.constants import MEDIA_TYPE_TO_ARR, TOOL_VERSION, ArrServiceName, MediaType, service_key
from arr_mcp.utils.jellyfin_bridge import JellyfinBridge

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
    jellyfin = JellyfinBridge(
        base_url=config.jellyfin.url,
        api_key=config.jellyfin.api_key,
        timeout=config.timeout,
    )

    @mcp.tool(
        annotations={"readOnlyHint": False, "destructiveHint": False},
        version=TOOL_VERSION,
    )
    async def arr_orchestrate(
        operation: Annotated[
            Literal["request", "status", "check_jellyfin", "queue"],
            Field(description="Operation: request a title, stack status, check Jellyfin, or show queue."),
        ],
        media_title: Annotated[str | None, Field(description="Media title for request/check_jellyfin.")] = None,
        media_type: Annotated[
            str | None,
            Field(description="Media type: 'movie', 'series', 'album', 'book'. Auto-detected if omitted."),
        ] = None,
        year: Annotated[int | None, Field(description="Year for disambiguation.")] = None,
        quality_profile_id: Annotated[int | None, Field(description="Quality profile ID for auto-add.")] = None,
        root_folder_path: Annotated[str | None, Field(description="Root folder path for auto-add.")] = None,
    ) -> dict:
        """Cross-arr orchestration: check Jellyfin, auto-route to correct arr, stack status.

        **THE DIFFERENTIATOR** — this tool chains Jellyfin availability check
        with automatic *arr routing.  "I want to watch Dune" → checks Jellyfin
        first → if not found → auto-adds to Radarr.

        ## Return Format
        {"success": bool, "message": str, "pipeline": [...], "data": {...}}

        ## Examples
        arr_orchestrate(operation="request", media_title="Dune")
        arr_orchestrate(operation="request", media_title="The Expanse", media_type="series")
        arr_orchestrate(operation="status")
        arr_orchestrate(operation="check_jellyfin", media_title="Inception")
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
                result = await jellyfin.check_availability(media_title, media_type=mt)
                return {
                    "success": True,
                    "message": f"{media_title} is {'IN' if result['in_library'] else 'NOT'} in Jellyfin",
                    "pipeline": ["jellyfin_check"],
                    "data": result,
                }

            if operation == "request":
                if not media_title:
                    return {"success": False, "message": "media_title is required", "pipeline": [], "data": {}}

                pipeline: list[str] = []

                # Step 1: Jellyfin availability check
                mt = MediaType(media_type) if media_type else None
                jf_result = await jellyfin.check_availability(media_title, media_type=mt)
                pipeline.append("jellyfin_check")

                if jf_result["in_library"]:
                    return {
                        "success": True,
                        "message": f"'{media_title}' is already available in your Jellyfin library.",
                        "pipeline": pipeline,
                        "data": {"in_library": True, "source": "jellyfin", **jf_result},
                    }

                # Step 2: Auto-detect media type if not specified
                if not mt:
                    mt = await _detect_media_type(media_title, clients)
                    pipeline.append("type_detection")

                if mt is None:
                    return {
                        "success": False,
                        "message": f"Could not determine media type for '{media_title}'. Try specifying media_type.",
                        "pipeline": pipeline,
                        "data": {},
                    }

                # Step 3: Check if already in the arr
                arr_name = MEDIA_TYPE_TO_ARR.get(mt)
                arr_client = clients.get(arr_name) if arr_name else None

                if arr_client is None:
                    return {
                        "success": False,
                        "message": f"{service_key(arr_name) if arr_name else mt.value} is not configured.",
                        "pipeline": pipeline,
                        "data": {},
                    }

                # Check if already queued/wanted
                existing = await _check_already_queued(arr_client, media_title, mt)
                pipeline.append("queue_check")

                if existing:
                    return {
                        "success": True,
                        "message": f"'{media_title}' is already in {service_key(arr_name)} ({existing}).",
                        "pipeline": pipeline,
                        "data": {
                            "in_library": False,
                            "already_queued": True,
                            "arr": service_key(arr_name),
                            "detail": existing,
                        },
                    }

                # Step 4: Queue in appropriate arr
                add_result = await _add_to_arr(arr_client, media_title, mt, quality_profile_id, root_folder_path)
                pipeline.append("add_to_arr")

                return {
                    "success": True,
                    "message": f"'{media_title}' added to {service_key(arr_name)}.",
                    "pipeline": pipeline,
                    "data": {
                        "in_library": False,
                        "action": f"added_to_{service_key(arr_name)}",
                        "media_type": mt.value,
                        "add_result": add_result,
                    },
                }

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
                end_of_week = (
                    now.replace(hour=23, minute=59, second=59)
                    + (now.replace(hour=0, minute=0, second=0) - now)
                    + (  # type: ignore[operator]
                        __import__("datetime").timedelta(days=6)
                    )
                )
                end_str = end_of_week.strftime("%Y-%m-%dT23:59:59Z")
            elif operation == "range":
                start_str = start or now.strftime("%Y-%m-%dT00:00:00Z")
                end_str = end or now.strftime("%Y-%m-%dT23:59:59Z")
            else:
                start_str = now.strftime("%Y-%m-%dT00:00:00Z")
                end_str = (now + __import__("datetime").timedelta(days=30)).strftime("%Y-%m-%dT23:59:59Z")

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


async def _detect_media_type(title: str, clients: dict) -> MediaType | None:
    """Auto-detect media type by trying lookups across all configured arrs."""
    lookup_map = [
        (MediaType.MOVIE, clients.get(ArrServiceName.RADARR), "lookup_movie"),
        (MediaType.SERIES, clients.get(ArrServiceName.SONARR), "lookup_series"),
        (MediaType.ALBUM, clients.get(ArrServiceName.LIDARR), "lookup_artist"),
        (MediaType.BOOK, clients.get(ArrServiceName.READARR), "lookup_author"),
    ]

    for mt, client, method_name in lookup_map:
        if client is None:
            continue
        try:
            method = getattr(client, method_name)
            results = await method(title)
            if results and len(results) > 0:
                return mt
        except Exception as exc:
            logger.debug("Type detection for '%s' failed: %s", title, exc)
            continue

    return None


async def _check_already_queued(client, title: str, media_type: MediaType) -> dict | None:
    """Check if title is already wanted/queued in the arr."""
    try:
        wanted = await client.get_wanted_missing()
        records: list[dict] = wanted.get("records", [])
        title_lower = title.lower()

        for record in records:
            record_title = (
                record.get("title")
                or record.get("series", {}).get("title", "")
                or record.get("artist", {}).get("artistName", "")
                or record.get("author", {}).get("authorName", "")
            )
            if record_title and title_lower in record_title.lower():
                return record

        return None
    except Exception:
        return None


async def _add_to_arr(
    client,
    title: str,
    media_type: MediaType,
    quality_profile_id: int | None = None,
    root_folder_path: str | None = None,
) -> dict:
    """Add title to the appropriate arr."""
    # First lookup the item
    lookup_methods = {
        MediaType.MOVIE: ("lookup_movie", "add_movie", "tmdbId", "title"),
        MediaType.SERIES: ("lookup_series", "add_series", "tvdbId", "title"),
        MediaType.ALBUM: ("lookup_artist", "add_artist", "foreignArtistId", "artistName"),
        MediaType.BOOK: ("lookup_author", "add_author", "foreignAuthorId", "authorName"),
    }

    lookup_meta = lookup_methods.get(media_type)
    if not lookup_meta:
        return {"error": f"Unsupported media type: {media_type}"}

    lookup_method_name, add_method_name, id_field, title_field = lookup_meta
    lookup_method = getattr(client, lookup_method_name)
    add_method = getattr(client, add_method_name)

    results = await lookup_method(title)
    if not results:
        return {"error": f"No results found for '{title}'"}

    first = results[0]

    # Resolve quality profile and root folder if not provided
    if not quality_profile_id:
        try:
            profiles = await client.get_quality_profiles()
            if profiles:
                quality_profile_id = profiles[0]["id"]
        except Exception:
            quality_profile_id = 1

    if not root_folder_path:
        try:
            folders = await client.get_root_folders()
            if folders:
                root_folder_path = folders[0]["path"]
        except Exception:
            root_folder_path = "/data"

    kwargs: dict = {
        id_field: first.get(id_field),
        title_field: first.get(title_field, title),
        "quality_profile_id": quality_profile_id,
        "root_folder_path": root_folder_path,
    }

    return await add_method(**kwargs)


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
