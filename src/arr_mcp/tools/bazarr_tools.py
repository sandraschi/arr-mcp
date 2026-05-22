"""Bazarr portmanteau tool — subtitle management.

Bazarr is NOT Servarr-based — it connects to Sonarr/Radarr for media metadata
and manages subtitle download from various providers.  This tool feeds
jellyfin-mcp's RAG pipeline downstream.
"""

from __future__ import annotations

import logging
from typing import Annotated, Literal

from pydantic import Field

from arr_mcp.constants import TOOL_VERSION

logger = logging.getLogger(__name__)


def register_bazarr_tools(mcp, client) -> None:
    if client is None:
        logger.info("Bazarr not configured — skipping tools")
        return

    @mcp.tool(
        annotations={"readOnlyHint": False, "destructiveHint": False},
        version=TOOL_VERSION,
    )
    async def bazarr_subtitles(
        operation: Annotated[
            Literal["wanted", "search", "download", "history", "providers", "languages"],
            Field(description="Operation: wanted (missing), search, download, history, providers, languages."),
        ],
        episode_id: Annotated[int | None, Field(description="Episode ID for search/download.")] = None,
        movie_id: Annotated[int | None, Field(description="Movie ID for search/download.")] = None,
        language: Annotated[str | None, Field(description="Subtitle language code (e.g. 'en', 'de').")] = None,
        subtitle_path: Annotated[
            str | None, Field(description="Subtitle path from search results for download.")
        ] = None,
        provider: Annotated[str | None, Field(description="Provider name for download.")] = None,
        scene_name: Annotated[str | None, Field(description="Scene name for download.")] = None,
    ) -> dict:
        """Manage Bazarr subtitles: wanted list, search, download, history, providers.

        Bazarr is the subtitle automation companion for the *arr stack.
        Results from this tool can feed jellyfin-mcp's RAG pipeline for
        downstream subtitle quality analysis.

        ## Return Format
        {"success": bool, "message": str, "data": [...]}

        ## Examples
        bazarr_subtitles(operation="wanted")
        bazarr_subtitles(operation="search", episode_id=123, language="en")
        bazarr_subtitles(operation="download", episode_id=123, subtitle_path="/subs/eng.srt", language="en", provider="opensubtitles")
        bazarr_subtitles(operation="history")
        bazarr_subtitles(operation="providers")
        """
        try:
            if operation == "wanted":
                data = await client.get_all_wanted()
                total = len(data.get("movies", {}).get("data", [])) + len(data.get("episodes", {}).get("data", []))
                return {"success": True, "message": f"Found {total} items with missing subtitles", "data": data}

            if operation == "search":
                if not episode_id and not movie_id:
                    return {"success": False, "message": "episode_id or movie_id is required for search", "data": []}
                data = await client.search_subtitles(episode_id=episode_id, movie_id=movie_id, language=language)
                return {"success": True, "message": f"Found {len(data)} subtitle results", "data": data}

            if operation == "download":
                if not subtitle_path:
                    return {"success": False, "message": "subtitle_path is required for download", "data": {}}
                if not episode_id and not movie_id:
                    return {"success": False, "message": "episode_id or movie_id is required for download", "data": {}}
                data = await client.download_subtitle(
                    subtitle_path=subtitle_path,
                    episode_id=episode_id,
                    movie_id=movie_id,
                    language=language,
                    provider=provider,
                    scene_name=scene_name,
                )
                return {"success": True, "message": "Subtitle download triggered", "data": data}

            if operation == "history":
                data = await client.get_history()
                return {"success": True, "message": f"Found {len(data)} history entries", "data": data}

            if operation == "providers":
                data = await client.get_providers()
                return {"success": True, "message": f"Found {len(data)} subtitle providers", "data": data}

            if operation == "languages":
                data = await client.get_languages()
                return {"success": True, "message": f"Found {len(data)} language profiles", "data": data}

            return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            logger.exception("bazarr_subtitles failed: %s", e)
            return {"success": False, "message": str(e), "data": {}}
