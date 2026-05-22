"""Lidarr portmanteau tools — artist & album management."""

from __future__ import annotations

import logging
from typing import Annotated, Literal

from pydantic import Field

from arr_mcp.constants import TOOL_VERSION

logger = logging.getLogger(__name__)


def register_lidarr_tools(mcp, client) -> None:
    if client is None:
        logger.info("Lidarr not configured — skipping tools")
        return

    @mcp.tool(
        annotations={"readOnlyHint": False, "destructiveHint": False},
        version=TOOL_VERSION,
    )
    async def lidarr_artists(
        operation: Annotated[
            Literal["list", "lookup", "get", "add", "delete", "update"],
            Field(description="Operation: list all, lookup by term, get by ID, add, delete, or update."),
        ],
        term: Annotated[str | None, Field(description="Search term for lookup.")] = None,
        artist_id: Annotated[int | None, Field(description="Artist ID for get/delete/update.")] = None,
        foreign_artist_id: Annotated[str | None, Field(description="MusicBrainz ID for add.")] = None,
        quality_profile_id: Annotated[int | None, Field(description="Quality profile ID for add.")] = None,
        root_folder_path: Annotated[str | None, Field(description="Root folder path for add.")] = None,
        monitored: Annotated[bool, Field(description="Monitored status for add/update.")] = True,
        delete_files: Annotated[bool, Field(description="Also delete files when deleting artist.")] = False,
    ) -> dict:
        """Manage Lidarr artists: list, search, add, delete, update.

        ## Return Format
        {"success": bool, "message": str, "data": [...]}

        ## Examples
        lidarr_artists(operation="list")
        lidarr_artists(operation="lookup", term="NIN")
        lidarr_artists(operation="add", foreign_artist_id="abc-123", quality_profile_id=1, root_folder_path="/music")
        """
        try:
            if operation == "list":
                data = await client.get_artists()
                return {"success": True, "message": f"Found {len(data)} artists", "data": data}

            if operation == "lookup":
                if not term:
                    return {"success": False, "message": "term is required for lookup", "data": []}
                data = await client.lookup_artist(term)
                return {"success": True, "message": f"Found {len(data)} results for '{term}'", "data": data}

            if operation == "get":
                if not artist_id:
                    return {"success": False, "message": "artist_id is required for get", "data": {}}
                data = await client.get_artist(artist_id)
                return {"success": True, "message": f"Artist {artist_id}", "data": data}

            if operation == "add":
                if not foreign_artist_id or not quality_profile_id or not root_folder_path:
                    return {
                        "success": False,
                        "message": "foreign_artist_id, quality_profile_id, and root_folder_path are required",
                        "data": {},
                    }
                data = await client.add_artist(
                    foreign_artist_id=foreign_artist_id,
                    quality_profile_id=quality_profile_id,
                    root_folder_path=root_folder_path,
                    monitored=monitored,
                )
                return {"success": True, "message": f"Added artist '{data.get('artistName', '')}'", "data": data}

            if operation == "delete":
                if not artist_id:
                    return {"success": False, "message": "artist_id is required for delete", "data": {}}
                await client.delete_artist(artist_id, delete_files=delete_files)
                return {"success": True, "message": f"Deleted artist {artist_id}", "data": {}}

            if operation == "update":
                if not artist_id:
                    return {"success": False, "message": "artist_id is required for update", "data": {}}
                data = await client.update_artist(artist_id, monitored=monitored)
                return {"success": True, "message": f"Updated artist {artist_id}", "data": data}

            return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            logger.exception("lidarr_artists failed: %s", e)
            return {"success": False, "message": str(e), "data": {}}

    @mcp.tool(
        annotations={"readOnlyHint": False, "destructiveHint": False},
        version=TOOL_VERSION,
    )
    async def lidarr_albums(
        operation: Annotated[
            Literal["list", "get", "lookup", "set_monitored"],
            Field(description="Operation: list albums, get by ID, lookup by term, set monitored status."),
        ],
        artist_id: Annotated[int | None, Field(description="Artist ID for listing albums.")] = None,
        album_id: Annotated[int | None, Field(description="Album ID for get/set_monitored.")] = None,
        term: Annotated[str | None, Field(description="Search term for lookup.")] = None,
        monitored: Annotated[bool, Field(description="Monitored status for set_monitored.")] = True,
    ) -> dict:
        """Manage Lidarr albums: list, get, lookup, set monitored.

        ## Return Format
        {"success": bool, "message": str, "data": [...]}

        ## Examples
        lidarr_albums(operation="list", artist_id=1)
        lidarr_albums(operation="lookup", term="The Downward Spiral")
        lidarr_albums(operation="set_monitored", album_id=5, monitored=False)
        """
        try:
            if operation == "list":
                data = await client.get_albums(artist_id=artist_id)
                return {"success": True, "message": f"Found {len(data)} albums", "data": data}

            if operation == "get":
                if not album_id:
                    return {"success": False, "message": "album_id is required for get", "data": {}}
                data = await client.get_album(album_id)
                return {"success": True, "message": f"Album {album_id}", "data": data}

            if operation == "lookup":
                if not term:
                    return {"success": False, "message": "term is required for lookup", "data": []}
                data = await client.lookup_album(term)
                return {"success": True, "message": f"Found {len(data)} results for '{term}'", "data": data}

            if operation == "set_monitored":
                if not album_id:
                    return {"success": False, "message": "album_id is required for set_monitored", "data": {}}
                await client.set_albums_monitored([album_id], monitored)
                return {"success": True, "message": f"Album {album_id} monitored={monitored}", "data": {}}

            return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            logger.exception("lidarr_albums failed: %s", e)
            return {"success": False, "message": str(e), "data": {}}
