"""Radarr portmanteau tool — movie management.

All Radarr operations consolidated into a single ``radarr_movies`` tool with an
``operation`` discriminator.  Registered at import time via ``@mcp.tool()``
decorator.
"""

from __future__ import annotations

import logging
from typing import Annotated, Literal

from pydantic import Field, StrictInt

from arr_mcp.constants import TOOL_VERSION

logger = logging.getLogger(__name__)


def register_radarr_tools(mcp, client) -> None:
    """Register Radarr tools on the FastMCP instance."""
    if client is None:
        logger.info("Radarr not configured — skipping tools")
        return

    @mcp.tool(
        annotations={"readOnlyHint": False, "destructiveHint": False},
        version=TOOL_VERSION,
    )
    async def radarr_movies(
        operation: Annotated[
            Literal["list", "lookup", "get", "add", "search", "delete", "update", "import"],
            Field(
                description="Operation: list all, lookup by term, get by ID, add, search, delete, update, or import."
            ),
        ],
        term: Annotated[str | None, Field(description="Search term for lookup or add.")] = None,
        movie_id: Annotated[
            StrictInt | None, Field(description="Exact Radarr movie ID for get/search/delete/update.")
        ] = None,
        tmdb_id: Annotated[int | None, Field(description="TMDB ID for add operation.")] = None,
        title: Annotated[str | None, Field(description="Movie title for add operation.")] = None,
        quality_profile_id: Annotated[int | None, Field(description="Quality profile ID for add.")] = None,
        root_folder_path: Annotated[str | None, Field(description="Root folder path for add.")] = None,
        monitored: Annotated[bool, Field(description="Monitored status for add/update.")] = True,
        search_for_movie: Annotated[bool, Field(description="Search immediately after add.")] = True,
        delete_files: Annotated[bool, Field(description="Also delete files when deleting movie.")] = False,
        folder: Annotated[str | None, Field(description="Folder path for manual import.")] = None,
        add_import_list_exclusion: Annotated[
            bool, Field(description="When deleting, prevent import lists from adding this movie again. Defaults false.")
        ] = False,
    ) -> dict:
        """Manage Radarr movies: list, lookup, get, add, search, delete, update, import.

        ``lookup`` finds movie metadata. ``search`` starts Radarr's native
        MoviesSearch for one movie already in the library. The returned command
        confirms submission, not a completed download.

        On deletion, add_import_list_exclusion=true matches Add List Exclusion.
        This is independent of delete_files, which defaults to false.

        ## Return Format
        {"success": bool, "message": str, "data": [...]}

        ## Examples
        radarr_movies(operation="list")
        radarr_movies(operation="lookup", term="Dune")
        radarr_movies(operation="add", tmdb_id=438631, quality_profile_id=1, root_folder_path="/movies")
        radarr_movies(operation="search", movie_id=42)
        radarr_movies(operation="delete", movie_id=42, delete_files=True)
        radarr_movies(operation="delete", movie_id=42, add_import_list_exclusion=True)
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

            if operation == "search":
                if isinstance(movie_id, bool) or not isinstance(movie_id, int) or movie_id <= 0:
                    return {"success": False, "message": "A positive exact movie_id is required for search", "data": {}}
                movie = await client.get_movie(movie_id)
                if not isinstance(movie, dict) or type(movie.get("id")) is not int or movie["id"] != movie_id:
                    return {
                        "success": False,
                        "message": f"Radarr returned a mismatched movie ID for requested movie {movie_id}; search was not started",
                        "data": {},
                    }
                command = await client.trigger_command("MoviesSearch", movieIds=[movie_id])
                return {
                    "success": True,
                    "message": f"Submitted Radarr search for '{movie.get('title', movie_id)}' (movie {movie_id})",
                    "data": command,
                }

            if operation == "delete":
                if not movie_id:
                    return {"success": False, "message": "movie_id is required for delete", "data": {}}
                await client.delete_movie(
                    movie_id, delete_files=delete_files, add_import_list_exclusion=add_import_list_exclusion
                )
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
