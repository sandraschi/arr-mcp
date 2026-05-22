"""Sonarr portmanteau tools — series & episode management."""

from __future__ import annotations

import logging
from typing import Annotated, Literal

from pydantic import Field

from arr_mcp.constants import TOOL_VERSION

logger = logging.getLogger(__name__)


def register_sonarr_tools(mcp, client) -> None:
    if client is None:
        logger.info("Sonarr not configured — skipping tools")
        return

    @mcp.tool(
        annotations={"readOnlyHint": False, "destructiveHint": False},
        version=TOOL_VERSION,
    )
    async def sonarr_series(
        operation: Annotated[
            Literal["list", "lookup", "get", "add", "delete", "update"],
            Field(description="Operation: list all, lookup by term, get by ID, add, delete, or update."),
        ],
        term: Annotated[str | None, Field(description="Search term for lookup.")] = None,
        series_id: Annotated[int | None, Field(description="Series ID for get/delete/update.")] = None,
        tvdb_id: Annotated[int | None, Field(description="TVDB ID for add operation.")] = None,
        title: Annotated[str | None, Field(description="Series title for add.")] = None,
        quality_profile_id: Annotated[int | None, Field(description="Quality profile ID for add.")] = None,
        root_folder_path: Annotated[str | None, Field(description="Root folder path for add.")] = None,
        monitored: Annotated[bool, Field(description="Monitored status for add/update.")] = True,
        search_for_missing: Annotated[bool, Field(description="Search for missing episodes after add.")] = True,
        delete_files: Annotated[bool, Field(description="Also delete files when deleting series.")] = False,
    ) -> dict:
        """Manage Sonarr series: list, search, add, delete, update.

        ## Return Format
        {"success": bool, "message": str, "data": [...]}

        ## Examples
        sonarr_series(operation="list")
        sonarr_series(operation="lookup", term="Breaking Bad")
        sonarr_series(operation="add", tvdb_id=81189, quality_profile_id=1, root_folder_path="/tv")
        """
        try:
            if operation == "list":
                data = await client.get_series()
                return {"success": True, "message": f"Found {len(data)} series", "data": data}

            if operation == "lookup":
                if not term:
                    return {"success": False, "message": "term is required for lookup", "data": []}
                data = await client.lookup_series(term)
                return {"success": True, "message": f"Found {len(data)} results for '{term}'", "data": data}

            if operation == "get":
                if not series_id:
                    return {"success": False, "message": "series_id is required for get", "data": {}}
                data = await client.get_series_by_id(series_id)
                return {"success": True, "message": f"Series {series_id}", "data": data}

            if operation == "add":
                if not tvdb_id or not quality_profile_id or not root_folder_path:
                    return {
                        "success": False,
                        "message": "tvdb_id, quality_profile_id, and root_folder_path are required",
                        "data": {},
                    }
                data = await client.add_series(
                    tvdb_id=tvdb_id,
                    title=title or "",
                    quality_profile_id=quality_profile_id,
                    root_folder_path=root_folder_path,
                    monitored=monitored,
                    search_for_missing_episodes=search_for_missing,
                )
                return {"success": True, "message": f"Added '{title or data.get('title', '')}'", "data": data}

            if operation == "delete":
                if not series_id:
                    return {"success": False, "message": "series_id is required for delete", "data": {}}
                await client.delete_series(series_id, delete_files=delete_files)
                return {"success": True, "message": f"Deleted series {series_id}", "data": {}}

            if operation == "update":
                if not series_id:
                    return {"success": False, "message": "series_id is required for update", "data": {}}
                data = await client.update_series(series_id, monitored=monitored)
                return {"success": True, "message": f"Updated series {series_id}", "data": data}

            return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            logger.exception("sonarr_series failed: %s", e)
            return {"success": False, "message": str(e), "data": {}}

    @mcp.tool(
        annotations={"readOnlyHint": False, "destructiveHint": False},
        version=TOOL_VERSION,
    )
    async def sonarr_episodes(
        operation: Annotated[
            Literal["list", "get", "search", "set_monitored"],
            Field(description="Operation: list episodes, get by ID, trigger episode search, set monitored status."),
        ],
        series_id: Annotated[int | None, Field(description="Series ID for listing episodes.")] = None,
        season_number: Annotated[int | None, Field(description="Season number for filtering episodes.")] = None,
        episode_id: Annotated[int | None, Field(description="Episode ID for get/search/set_monitored.")] = None,
        monitored: Annotated[bool, Field(description="Monitored status for set_monitored.")] = True,
    ) -> dict:
        """Manage Sonarr episodes: list, get, trigger search, set monitored.

        ## Return Format
        {"success": bool, "message": str, "data": [...]}

        ## Examples
        sonarr_episodes(operation="list", series_id=123)
        sonarr_episodes(operation="search", episode_id=456)
        sonarr_episodes(operation="set_monitored", episode_id=456, monitored=False)
        """
        try:
            if operation == "list":
                if not series_id:
                    return {"success": False, "message": "series_id is required for list", "data": []}
                data = await client.get_episodes(series_id, season_number=season_number)
                return {"success": True, "message": f"Found {len(data)} episodes", "data": data}

            if operation == "get":
                if not episode_id:
                    return {"success": False, "message": "episode_id is required for get", "data": {}}
                data = await client.get_episode(episode_id)
                return {"success": True, "message": f"Episode {episode_id}", "data": data}

            if operation == "search":
                if not episode_id:
                    return {"success": False, "message": "episode_id is required for search", "data": {}}
                result = await client.trigger_command("EpisodeSearch", episodeIds=[episode_id])
                return {"success": True, "message": f"Triggered search for episode {episode_id}", "data": result}

            if operation == "set_monitored":
                if not episode_id:
                    return {"success": False, "message": "episode_id is required for set_monitored", "data": {}}
                data = await client.update_episode(episode_id, monitored=monitored)
                return {"success": True, "message": f"Episode {episode_id} monitored={monitored}", "data": data}

            return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            logger.exception("sonarr_episodes failed: %s", e)
            return {"success": False, "message": str(e), "data": {}}
