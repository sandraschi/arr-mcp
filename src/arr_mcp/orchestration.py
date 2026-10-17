"""Shared cross-arr orchestration pipeline.

The media-request pipeline used to live inside the ``arr_orchestrate`` MCP tool
closure, which meant the webapp could describe it but never run it. This module
hosts the pipeline plus its helpers so both the MCP tool
(``tools/cross_arr_tools.py``) and the REST endpoint
(``POST /api/orchestrate/request``) execute identical logic.
"""

from __future__ import annotations

import logging
from typing import Any

from arr_mcp.constants import MEDIA_TYPE_TO_ARR, MediaType, service_key
from arr_mcp.utils.emby_bridge import EmbyBridge
from arr_mcp.utils.jellyfin_bridge import JellyfinBridge
from arr_mcp.utils.plex_bridge import PlexBridge

logger = logging.getLogger(__name__)


def build_bridges(config) -> dict[str, Any]:
    """Build media-server bridges from the full ArrConfig."""
    return {
        "jellyfin": JellyfinBridge(
            base_url=config.jellyfin.url,
            api_key=config.jellyfin.api_key,
            timeout=config.timeout,
        ),
        "plex": PlexBridge(
            base_url=config.plex.url,
            token=config.plex.token,
            timeout=config.timeout,
        ),
        "emby": EmbyBridge(
            base_url=config.emby.url,
            api_key=config.emby.api_key,
            timeout=config.timeout,
        ),
    }


async def request_media(
    clients: dict,
    bridges: dict[str, Any],
    media_title: str,
    media_type: str | None = None,
    quality_profile_id: int | None = None,
    root_folder_path: str | None = None,
    media_server: str | None = None,
) -> dict:
    """Run the request pipeline: library check → type detect → queue check → add.

    Returns the same ``{"success", "message", "pipeline", "data"}`` shape as
    ``arr_orchestrate(operation="request", ...)``.
    """
    jellyfin = bridges.get("jellyfin")
    plex = bridges.get("plex")
    emby = bridges.get("emby")

    pipeline: list[str] = []
    mt = MediaType(media_type) if media_type else None

    # Step 1: Media server availability check
    servers_to_check: list[tuple[str, Any, str]] = []
    if (media_server is None or media_server == "jellyfin") and jellyfin is not None:
        servers_to_check.append(("jellyfin", jellyfin, "jellyfin_check"))
    if (media_server is None or media_server == "plex") and plex is not None:
        servers_to_check.append(("plex", plex, "plex_check"))
    if (media_server is None or media_server == "emby") and emby is not None:
        servers_to_check.append(("emby", emby, "emby_check"))

    for server_name, bridge, step_label in servers_to_check:
        if bridge.is_configured:
            try:
                result = await bridge.check_availability(media_title, media_type=mt)
            except Exception as exc:
                # A configured-but-unreachable media server must not abort
                # the whole orchestration (issue #1: Emby errors out).
                logger.warning("%s check failed for '%s': %s", server_name, media_title, exc)
                pipeline.append(f"{step_label}_error")
                continue
            pipeline.append(step_label)
            if result["in_library"]:
                return {
                    "success": True,
                    "message": f"'{media_title}' is already available in your {server_name.title()} library.",
                    "pipeline": pipeline,
                    "data": {"in_library": True, "source": server_name, **result},
                }
        else:
            pipeline.append(f"{server_name}_not_configured")

    # Step 2: Auto-detect media type if not specified
    if not mt:
        mt = await detect_media_type(media_title, clients)
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
    existing = await check_already_queued(arr_client, media_title, mt)
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
    add_result = await add_to_arr(arr_client, media_title, mt, quality_profile_id, root_folder_path)
    pipeline.append("add_to_arr")

    if isinstance(add_result, dict) and add_result.get("error"):
        return {
            "success": False,
            "message": f"Could not add '{media_title}' to {service_key(arr_name)}: {add_result['error']}",
            "pipeline": pipeline,
            "data": {
                "in_library": False,
                "action": f"add_to_{service_key(arr_name)}_failed",
                "media_type": mt.value,
                "add_result": add_result,
            },
        }

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


async def detect_media_type(title: str, clients: dict) -> MediaType | None:
    """Auto-detect media type by trying lookups across all configured arrs."""
    lookup_map = [
        (MediaType.MOVIE, clients.get("radarr"), "lookup_movie"),
        (MediaType.SERIES, clients.get("sonarr"), "lookup_series"),
        (MediaType.ALBUM, clients.get("lidarr"), "lookup_artist"),
        (MediaType.BOOK, clients.get("readarr"), "lookup_author"),
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


async def check_already_queued(client, title: str, media_type: MediaType) -> dict | None:
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


async def add_to_arr(
    client,
    title: str,
    media_type: MediaType,
    quality_profile_id: int | None = None,
    root_folder_path: str | None = None,
) -> dict:
    """Add title to the appropriate arr."""
    # First lookup the item. Client methods take snake_case params; the
    # lookup payloads use Servarr camelCase keys — never mix the two (the
    # **kwargs catch-alls swallow unknown names and required positionals
    # then go missing, which mocks never catch).
    lookup_methods = {
        MediaType.MOVIE: ("lookup_movie", "add_movie", "tmdbId", "tmdb_id", "title", True),
        MediaType.SERIES: ("lookup_series", "add_series", "tvdbId", "tvdb_id", "title", True),
        MediaType.ALBUM: ("lookup_artist", "add_artist", "foreignArtistId", "foreign_artist_id", None, False),
        MediaType.BOOK: ("lookup_author", "add_author", "foreignAuthorId", "foreign_author_id", None, False),
    }

    lookup_meta = lookup_methods.get(media_type)
    if not lookup_meta:
        return {"error": f"Unsupported media type: {media_type}"}

    lookup_method_name, add_method_name, id_field, id_param, title_field, takes_title = lookup_meta
    lookup_method = getattr(client, lookup_method_name)
    add_method = getattr(client, add_method_name)

    results = await lookup_method(title)
    if not results:
        return {"error": f"No results found for '{title}'"}

    first = results[0]
    foreign_id = first.get(id_field)
    if not foreign_id:
        return {"error": f"Lookup result for '{title}' has no {id_field}"}

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
        except Exception as exc:
            logger.debug("Root folder lookup failed: %s", exc)

    if not root_folder_path:
        return {
            "error": (
                "no root folder configured — add one in the service UI under "
                "Settings → Media Management (e.g. /movies on compose), then retry"
            )
        }

    kwargs: dict = {
        id_param: foreign_id,
        "quality_profile_id": quality_profile_id,
        "root_folder_path": root_folder_path,
    }
    if takes_title and title_field:
        kwargs["title"] = first.get(title_field, title)

    try:
        return await add_method(**kwargs)
    except Exception as exc:
        return {"error": f"{add_method.__name__} failed: {exc}"}
