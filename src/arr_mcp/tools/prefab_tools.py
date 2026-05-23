"""Prefab-UI card tools for arr-mcp.

Registers MCP tools that return rich Prefab cards for health status,
calendar, orchestration results, and stack statistics.
"""

from __future__ import annotations

import logging
from typing import Annotated

from pydantic import Field

from arr_mcp.constants import TOOL_VERSION
from arr_mcp.prefabs import (
    build_calendar_card,
    build_health_card,
    build_stats_card,
)

logger = logging.getLogger(__name__)


def register_prefab_tools(mcp, clients: dict) -> None:
    """Register Prefab card tools on the FastMCP instance."""

    @mcp.tool(
        annotations={"readOnlyHint": True, "destructiveHint": False},
        version=TOOL_VERSION,
    )
    async def arr_health_card() -> dict:
        """Show the *arr stack health as a rich Prefab card.

        Returns a PrefabApp card showing reachability and version for every
        configured *arr service. Equivalent to `arr_health(service='all')`
        but rendered as a visual card in supporting MCP clients.

        ## Return Format
        PrefabApp card with service status table, or dict if Prefab not supported.

        ## Examples
        arr_health_card()
        """
        health_data: dict[str, dict] = {}
        for name, client in clients.items():
            if client is None:
                health_data[name] = {"reachable": False, "version": None}
                continue
            try:
                status = await client.health_check()
                health_data[name] = {
                    "reachable": True,
                    "version": status.get("version"),
                }
            except Exception:
                health_data[name] = {"reachable": False, "version": None}

        result = {
            "success": True,
            "message": "Stack health card",
            "data": health_data,
        }
        return build_health_card(result)

    @mcp.tool(
        annotations={"readOnlyHint": True, "destructiveHint": False},
        version=TOOL_VERSION,
    )
    async def arr_calendar_card(
        days: Annotated[int, Field(description="Number of days to look ahead.", ge=1, le=90)] = 14,
    ) -> dict:
        """Show upcoming releases as a rich Prefab calendar card.

        Aggregates upcoming releases from Radarr, Sonarr, Lidarr, and Readarr
        into a single visual card.

        ## Return Format
        PrefabApp card with upcoming release table.

        ## Examples
        arr_calendar_card()
        arr_calendar_card(days=30)
        """
        from datetime import UTC, datetime, timedelta

        now = datetime.now(UTC)
        start_str = now.strftime("%Y-%m-%dT00:00:00Z")
        end_str = (now + timedelta(days=days)).strftime("%Y-%m-%dT23:59:59Z")

        results: dict[str, list[dict]] = {}
        calendar_clients = {
            "radarr": clients.get("radarr"),
            "sonarr": clients.get("sonarr"),
            "lidarr": clients.get("lidarr"),
            "readarr": clients.get("readarr"),
        }

        for name, client in calendar_clients.items():
            if client is None:
                continue
            try:
                data = await client.get_calendar(start=start_str, end=end_str)
                results[name] = data
            except Exception:
                results[name] = []

        total = sum(len(v) for v in results.values())
        calendar_result = {
            "success": True,
            "message": f"Found {total} upcoming items",
            "data": results,
        }
        return build_calendar_card(calendar_result)

    @mcp.tool(
        annotations={"readOnlyHint": True, "destructiveHint": False},
        version=TOOL_VERSION,
    )
    async def arr_stats_card() -> dict:
        """Show consolidated stack statistics as a rich Prefab card.

        Returns a PrefabApp card with media counts and wanted/missing per service.

        ## Return Format
        PrefabApp card with stack statistics table.

        ## Examples
        arr_stats_card()
        """
        result: dict[str, dict] = {}
        stats_targets = [
            ("radarr", clients.get("radarr"), "get_movies", "movies"),
            ("sonarr", clients.get("sonarr"), "get_series", "series"),
            ("lidarr", clients.get("lidarr"), "get_artists", "artists"),
            ("readarr", clients.get("readarr"), "get_authors", "authors"),
        ]

        for name, client, method_name, label in stats_targets:
            if client is None:
                result[name] = {"enabled": False, label: 0, "wanted": 0}
                continue
            try:
                method = getattr(client, method_name)
                items = await method()
                wanted = await client.get_wanted_missing()
                result[name] = {
                    "enabled": True,
                    label: len(items),
                    "wanted": wanted.get("totalRecords", len(wanted.get("records", []))),
                }
            except Exception as exc:
                result[name] = {"enabled": True, label: 0, "wanted": 0, "error": str(exc)}

        stats_result = {
            "success": True,
            "message": "Stack statistics card",
            "data": result,
        }
        return build_stats_card(stats_result)
