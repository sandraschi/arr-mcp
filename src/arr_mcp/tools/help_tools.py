"""Tool discovery and quickstart — ``arr_help``.

Provides a single ``arr_help`` portmanteau tool that agents and users can call
to discover available tools, get per-tool documentation, or a quickstart guide.
"""

from __future__ import annotations

import logging
from typing import Annotated, Any, Literal

from pydantic import Field

from arr_mcp.constants import TOOL_VERSION

logger = logging.getLogger(__name__)

_TOOL_REGISTRY: dict[str, dict[str, Any]] = {
    "arr_radarr": {
        "description": "Radarr movie management — list, lookup, add, delete, update, import.",
        "operations": ["list", "lookup", "get", "add", "delete", "update", "import"],
        "service": "radarr",
    },
    "arr_sonarr_series": {
        "description": "Sonarr series management — list, lookup, add, delete, update.",
        "operations": ["list", "lookup", "get", "add", "delete", "update"],
        "service": "sonarr",
    },
    "arr_sonarr_episodes": {
        "description": "Sonarr episode management — list, get, search, set_monitored.",
        "operations": ["list", "get", "search", "set_monitored"],
        "service": "sonarr",
    },
    "arr_lidarr_artists": {
        "description": "Lidarr artist management — list, lookup, add, delete, update.",
        "operations": ["list", "lookup", "get", "add", "delete", "update"],
        "service": "lidarr",
    },
    "arr_lidarr_albums": {
        "description": "Lidarr album management — list, get, lookup, set_monitored.",
        "operations": ["list", "get", "lookup", "set_monitored"],
        "service": "lidarr",
    },
    "arr_readarr_authors": {
        "description": "Readarr author management — list, lookup, add, delete, update.",
        "operations": ["list", "lookup", "get", "add", "delete", "update"],
        "service": "readarr",
    },
    "arr_readarr_books": {
        "description": "Readarr book management — list, get, lookup, set_monitored.",
        "operations": ["list", "get", "lookup", "set_monitored"],
        "service": "readarr",
    },
    "arr_prowlarr_indexers": {
        "description": "Prowlarr indexer management — list, get, add, update, delete, test, test_all, schema.",
        "operations": ["list", "get", "add", "update", "delete", "test", "test_all", "schema"],
        "service": "prowlarr",
    },
    "arr_prowlarr_search": {
        "description": "Unified search across all Prowlarr indexers.",
        "operations": ["search"],
        "service": "prowlarr",
    },
    "arr_prowlarr_applications": {
        "description": "Manage Prowlarr-synced *arr applications — list, get, sync, sync_all, test.",
        "operations": ["list", "get", "sync", "sync_all", "test"],
        "service": "prowlarr",
    },
    "arr_prowlarr_history": {
        "description": "Query Prowlarr grab/search history — list, since, by_indexer.",
        "operations": ["list", "since", "by_indexer"],
        "service": "prowlarr",
    },
    "arr_overseerr_requests": {
        "description": "Overseerr media request management — list, get, create, approve, decline, delete, count, pending.",
        "operations": ["list", "get", "create", "approve", "decline", "delete", "count", "pending"],
        "service": "overseerr",
    },
    "arr_overseerr_search": {
        "description": "Search Overseerr for media to request.",
        "operations": ["search"],
        "service": "overseerr",
    },
    "arr_overseerr_users": {
        "description": "List Overseerr users and their requests.",
        "operations": ["list", "get", "requests"],
        "service": "overseerr",
    },
    "arr_bazarr_subtitles": {
        "description": "Bazarr subtitle management — wanted, search, download, history, providers, languages.",
        "operations": ["wanted", "search", "download", "history", "providers", "languages"],
        "service": "bazarr",
    },
    "arr_health": {
        "description": "Stack-wide health check — probes all configured services.",
        "operations": ["all", "radarr", "sonarr", "lidarr", "prowlarr", "readarr", "overseerr", "bazarr"],
        "service": "all",
    },
    "arr_orchestrate": {
        "description": "Cross-arr orchestration with Jellyfin availability check. The differentiator.",
        "operations": ["request", "status", "check_jellyfin", "queue"],
        "service": "orchestrator",
    },
    "arr_calendar": {
        "description": "Unified calendar across all *arr services.",
        "operations": ["upcoming", "today", "week", "range"],
        "service": "orchestrator",
    },
    "arr_stats": {
        "description": "Consolidated stack statistics — summary, disk, queues, history.",
        "operations": ["summary", "disk", "queues", "history"],
        "service": "orchestrator",
    },
    "arr_help": {
        "description": "Tool discovery and quickstart for the *arr stack.",
        "operations": ["discover", "tool_info", "quickstart"],
        "service": "system",
    },
    "arr_agentic": {
        "description": "LLM-sampled cross-arr workflows. Requires a sampling-capable MCP client.",
        "operations": ["workflow", "natural_query"],
        "service": "system",
    },
}


def register_help_tools(mcp) -> None:
    """Register the ``arr_help`` tool on the FastMCP instance."""

    @mcp.tool(
        annotations={"readOnlyHint": True, "destructiveHint": False},
        version=TOOL_VERSION,
    )
    async def arr_help(
        operation: Annotated[
            Literal["discover", "tool_info", "quickstart"],
            Field(
                description="Operation: discover available tools, get info about a specific tool, or quickstart guide."
            ),
        ],
        tool_name: Annotated[
            str | None, Field(description="Tool name for 'tool_info' operation, e.g. 'arr_orchestrate'.")
        ] = None,
    ) -> dict:
        """Discover and learn about arr-mcp tools.

        **discover** — list all registered tools with their operations.
        **tool_info** — get detailed documentation for a specific tool.
        **quickstart** — step-by-step guide to start using arr-mcp.

        ## Return Format
        {"success": bool, "message": str, "data": {"tools": [...], "tool_count": int} | {"info": ...} | {"steps": [...]}}

        ## Examples
        arr_help(operation="discover")
        arr_help(operation="tool_info", tool_name="arr_orchestrate")
        arr_help(operation="quickstart")
        """
        try:
            if operation == "discover":
                tools_list = [
                    {
                        "name": name,
                        "description": meta["description"],
                        "operations": meta["operations"],
                        "service": meta["service"],
                    }
                    for name, meta in _TOOL_REGISTRY.items()
                ]
                return {
                    "success": True,
                    "message": f"arr-mcp: {len(tools_list)} tools available",
                    "data": {
                        "tools": tools_list,
                        "tool_count": len(tools_list),
                        "version": TOOL_VERSION,
                    },
                }

            if operation == "tool_info":
                if not tool_name:
                    return {"success": False, "message": "tool_name is required for tool_info", "data": {}}

                meta = _TOOL_REGISTRY.get(tool_name)
                if meta is None:
                    return {
                        "success": False,
                        "message": f"Unknown tool '{tool_name}'. Use arr_help(operation='discover') to list all.",
                        "data": {},
                    }

                return {
                    "success": True,
                    "message": f"Documentation for {tool_name}",
                    "data": {"info": meta},
                }

            if operation == "quickstart":
                return {
                    "success": True,
                    "message": "arr-mcp quickstart guide",
                    "data": {
                        "steps": [
                            "1. Configure .env with your *arr URLs and API keys (see .env.example)",
                            "2. Run `uv sync` to install dependencies",
                            "3. Run `uv run arr-mcp` to start in STDIO mode (default)",
                            "4. Use `arr_health(service='all')` to verify connectivity",
                            "5. Use `arr_help(operation='discover')` to list available tools",
                            "6. For cross-arr orchestration: `arr_orchestrate(operation='request', media_title='Dune')`",
                            "7. For HTTP mode: `uv run arr-mcp --http --port 10938`",
                            "8. For stack health: `arr_health()`",
                        ],
                        "version": TOOL_VERSION,
                        "ports": {
                            "backend": 10938,
                            "frontend": 10939,
                        },
                    },
                }

            return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            logger.exception("arr_help failed: %s", e)
            return {"success": False, "message": str(e), "data": {}}
