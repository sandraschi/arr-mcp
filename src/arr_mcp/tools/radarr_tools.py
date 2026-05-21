"""Radarr portmanteau tool — movie management.

All Radarr operations consolidated into a single ``radarr_movies`` tool with an
``operation`` discriminator.  Registered at import time via ``@mcp.tool()``
decorator.
"""

from __future__ import annotations

import logging
from typing import Annotated, Literal

from pydantic import Field

logger = logging.getLogger(__name__)


def register_radarr_tools(mcp, client) -> None:
    """Register Radarr tools on the FastMCP instance."""
    if client is None:
        logger.info("Radarr not configured — skipping tools")
        return

    @mcp.tool(
        annotations={"readOnlyHint": False, "destructiveHint": False},
        version="0.1.0",
    )
    async def radarr_movies(
        operation: Annotated[
            Literal["list", "lookup", "get", "add", "delete", "update", "import"],
            Field(description="Operation: list all, lookup by term, get by ID, add, delete, update, or import."),
        ],
        term: Annotated[str | None, Field(description="Search term for lookup or add.")] = None,
        movie_id: Annotated[int | None, Field(description="Movie ID for get/delete/update.")] = None,
        tmdb_id: Annotated[int | None, Field(description="TMDB ID for add operation.")] = None,
        title: Annotated[str | None, Field(description="Movie title for add operation.")] = None,
        quality_profile_id: Annotated[int | None, Field(description="Quality profile ID for add.")] = None,
        root_folder_path: Annotated[str | None, Field(description="Root folder path for add.")] = None,
        monitored: Annotated[bool, Field(description="Monitored status for add/update.")] = True,
        search_for_movie: Annotated[bool, Field(description="Search immediately after add.")] = True,
        delete_files: Annotated[bool, Field(description="Also delete files when deleting movie.")] = False,
        folder: Annotated[str | None, Field(description="Folder path for manual import.")] = None,
    ) -> dict:
        """Manage Radarr movies: list, search, add, delete, import.

        ## Return Format
        {"success": bool, "message": str, "data": [...]}

        ## Examples
        radarr_movies(operation="list")
        radarr_movies(operation="lookup", term="Dune")
        radarr_movies(operation="add", tmdb_id=438631, quality_profile_id=1, root_folder_path="/movies")
        radarr_movies(operation="delete", movie_id=42, delete_files=True)
        """
        try:
            if operation == "list":
                data = await client.get_movies()
                return {"success": True, "message": f"Found {len(data)} movies", "data": data}

            if operation == "lookup":
                if not term:
                    return {"success": False, "message": "term is required for lookup", "data": []}
                data = await client.lookup_movie(term)
                return {"success": True, "message": f"Found {len(data)} results for '{term}'", "data": data}

            if operation == "get":
                if not movie_id:
                    return {"success": False, "message": "movie_id is required for get", "data": {}}
                data = await client.get_movie(movie_id)
                return {"success": True, "message": f"Movie {movie_id}", "data": data}

            if operation == "add":
                if not tmdb_id or not quality_profile_id or not root_folder_path:
                    return {
                        "success": False,
                        "message": "tmdb_id, quality_profile_id, and root_folder_path are required",
                        "data": {},
                    }
                data = await client.add_movie(
                    tmdb_id=tmdb_id,
                    title=title or "",
                    quality_profile_id=quality_profile_id,
                    root_folder_path=root_folder_path,
                    monitored=monitored,
                    search_for_movie=search_for_movie,
                )
                return {"success": True, "message": f"Added '{title or data.get('title', '')}'", "data": data}

            if operation == "delete":
                if not movie_id:
                    return {"success": False, "message": "movie_id is required for delete", "data": {}}
                await client.delete_movie(movie_id, delete_files=delete_files)
                return {"success": True, "message": f"Deleted movie {movie_id}", "data": {}}

            if operation == "update":
                if not movie_id:
                    return {"success": False, "message": "movie_id is required for update", "data": {}}
                data = await client.update_movie(movie_id, monitored=monitored)
                return {"success": True, "message": f"Updated movie {movie_id}", "data": data}

            if operation == "import":
                data = await client.get_manual_import(folder=folder)
                return {"success": True, "message": f"Found {len(data)} items to import", "data": data}

            return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            logger.exception("radarr_movies failed: %s", e)
            return {"success": False, "message": str(e), "data": {}}
