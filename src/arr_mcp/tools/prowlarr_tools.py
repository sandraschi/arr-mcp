"""Prowlarr portmanteau tools — indexer backbone + unified search."""

from __future__ import annotations

import logging
from typing import Annotated, Literal

from pydantic import Field

from arr_mcp.constants import TOOL_VERSION

logger = logging.getLogger(__name__)


def register_prowlarr_tools(mcp, client) -> None:
    if client is None:
        logger.info("Prowlarr not configured — skipping tools")
        return

    @mcp.tool(
        annotations={"readOnlyHint": False, "destructiveHint": False},
        version=TOOL_VERSION,
    )
    async def prowlarr_indexers(
        operation: Annotated[
            Literal["list", "get", "add", "update", "delete", "test", "test_all", "schema"],
            Field(description="Operation: list, get, add, update, delete, test, test_all, schema."),
        ],
        indexer_id: Annotated[int | None, Field(description="Indexer ID for get/update/delete/test.")] = None,
        name: Annotated[str | None, Field(description="Indexer name for add/update.")] = None,
        enable_rss: Annotated[bool, Field(description="Enable RSS for add/update.")] = True,
        enable_search: Annotated[bool, Field(description="Enable search for add/update.")] = True,
        priority: Annotated[int, Field(description="Priority for add/update.")] = 25,
        config_contract: Annotated[
            str | None, Field(description="Config contract (e.g. 'NewznabSettings') for add.")
        ] = None,
    ) -> dict:
        """Manage Prowlarr indexers: list, get, add, update, delete, test.

        Prowlarr is the indexer backbone — these tools manage Usenet and Torrent
        indexers that feed the entire *arr stack.

        ## Return Format
        {"success": bool, "message": str, "data": [...]}

        ## Examples
        prowlarr_indexers(operation="list")
        prowlarr_indexers(operation="test", indexer_id=1)
        prowlarr_indexers(operation="test_all")
        """
        try:
            if operation == "list":
                data = await client.get_indexers()
                return {"success": True, "message": f"Found {len(data)} indexers", "data": data}

            if operation == "get":
                if not indexer_id:
                    return {"success": False, "message": "indexer_id is required for get", "data": {}}
                data = await client.get_indexer(indexer_id)
                return {"success": True, "message": f"Indexer {indexer_id}", "data": data}

            if operation == "add":
                if not name or not config_contract:
                    return {"success": False, "message": "name and config_contract are required for add", "data": {}}
                data = await client.add_indexer(
                    name=name,
                    enableRss=enable_rss,
                    enableSearch=enable_search,
                    priority=priority,
                    configContract=config_contract,
                )
                return {"success": True, "message": f"Added indexer '{name}'", "data": data}

            if operation == "update":
                if not indexer_id:
                    return {"success": False, "message": "indexer_id is required for update", "data": {}}
                data = await client.update_indexer(
                    indexer_id, enableRss=enable_rss, enableSearch=enable_search, priority=priority
                )
                return {"success": True, "message": f"Updated indexer {indexer_id}", "data": data}

            if operation == "delete":
                if not indexer_id:
                    return {"success": False, "message": "indexer_id is required for delete", "data": {}}
                await client.delete_indexer(indexer_id)
                return {"success": True, "message": f"Deleted indexer {indexer_id}", "data": {}}

            if operation == "test":
                if not indexer_id:
                    return {"success": False, "message": "indexer_id is required for test", "data": {}}
                data = await client.test_indexer(indexer_id)
                return {"success": True, "message": f"Tested indexer {indexer_id}", "data": data}

            if operation == "test_all":
                data = await client.test_all_indexers()
                return {"success": True, "message": "Tested all indexers", "data": data}

            if operation == "schema":
                data = await client.get_indexer_schema()
                return {"success": True, "message": f"Found {len(data)} indexer schemas", "data": data}

            return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            logger.exception("prowlarr_indexers failed: %s", e)
            return {"success": False, "message": str(e), "data": {}}

    @mcp.tool(
        annotations={"readOnlyHint": True, "destructiveHint": False},
        version=TOOL_VERSION,
    )
    async def prowlarr_search(
        query: Annotated[str, Field(description="Search query across all configured indexers.")],
        categories: Annotated[
            list[int] | None, Field(description="Prowlarr category IDs (2000=Movies, 5000=TV, 3000=Music, 7000=Books).")
        ] = None,
        indexer_ids: Annotated[list[int] | None, Field(description="Limit to specific indexer IDs.")] = None,
        search_type: Annotated[
            str,
            Field(
                description="Search type: 'search' for manual, 'tvsearch' for TV, 'movie' for movies, 'music' for music, 'book' for books."
            ),
        ] = "search",
        limit: Annotated[int, Field(description="Max results.")] = 50,
    ) -> dict:
        """Unified search across ALL Prowlarr indexers.

        This is the backbone search tool — it queries every configured indexer
        (Usenet + Torrent) in a single call and returns aggregated results.

        ## Return Format
        {"success": bool, "message": str, "data": [...]}

        ## Examples
        prowlarr_search(query="Dune 2021 1080p", categories=[2000])
        prowlarr_search(query="The.Expanse.S06", search_type="tvsearch", categories=[5000])
        prowlarr_search(query="NIN Downward Spiral FLAC", search_type="music", categories=[3000])
        """
        try:
            results = await client.search(
                query=query,
                categories=categories,
                indexer_ids=indexer_ids,
                search_type=search_type,
                limit=limit,
            )
            return {
                "success": True,
                "message": f"Found {len(results)} results for '{query}'",
                "data": results,
            }
        except Exception as e:
            logger.exception("prowlarr_search failed: %s", e)
            return {"success": False, "message": str(e), "data": []}

    @mcp.tool(
        annotations={"readOnlyHint": False, "destructiveHint": False},
        version=TOOL_VERSION,
    )
    async def prowlarr_applications(
        operation: Annotated[
            Literal["list", "get", "sync", "sync_all", "test"],
            Field(description="Operation: list, get, sync one, sync all, test."),
        ],
        app_id: Annotated[int | None, Field(description="Application ID for get/sync/test.")] = None,
    ) -> dict:
        """Manage Prowlarr applications (synced *arr instances).

        Applications are connected Radarr/Sonarr/Lidarr/Readarr instances that
        receive indexer configurations from Prowlarr.

        ## Return Format
        {"success": bool, "message": str, "data": [...]}

        ## Examples
        prowlarr_applications(operation="list")
        prowlarr_applications(operation="sync", app_id=1)
        prowlarr_applications(operation="sync_all")
        """
        try:
            if operation == "list":
                data = await client.get_applications()
                return {"success": True, "message": f"Found {len(data)} applications", "data": data}

            if operation == "get":
                if not app_id:
                    return {"success": False, "message": "app_id is required for get", "data": {}}
                data = await client.get_application(app_id)
                return {"success": True, "message": f"Application {app_id}", "data": data}

            if operation == "sync":
                if not app_id:
                    return {"success": False, "message": "app_id is required for sync", "data": {}}
                data = await client.sync_application(app_id)
                return {"success": True, "message": f"Synced application {app_id}", "data": data}

            if operation == "sync_all":
                data = await client.sync_all_applications()
                return {"success": True, "message": "Synced all applications", "data": data}

            if operation == "test":
                if not app_id:
                    return {"success": False, "message": "app_id is required for test", "data": {}}
                data = await client.test_application(app_id)
                return {"success": True, "message": f"Tested application {app_id}", "data": data}

            return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            logger.exception("prowlarr_applications failed: %s", e)
            return {"success": False, "message": str(e), "data": {}}

    @mcp.tool(
        annotations={"readOnlyHint": True, "destructiveHint": False},
        version=TOOL_VERSION,
    )
    async def prowlarr_history(
        operation: Annotated[
            Literal["list", "since", "by_indexer"],
            Field(description="Operation: list recent, since date, or by specific indexer."),
        ],
        date: Annotated[str | None, Field(description="ISO datetime for 'since' operation.")] = None,
        indexer_id: Annotated[int | None, Field(description="Indexer ID for 'by_indexer'.")] = None,
        limit: Annotated[int, Field(description="Max results.")] = 50,
    ) -> dict:
        """Query Prowlarr grab/search history.

        ## Return Format
        {"success": bool, "message": str, "data": [...]}

        ## Examples
        prowlarr_history(operation="list")
        prowlarr_history(operation="since", date="2026-05-01T00:00:00Z")
        prowlarr_history(operation="by_indexer", indexer_id=1, limit=20)
        """
        try:
            if operation == "list":
                data = await client.get_history(page_size=limit)
                return {
                    "success": True,
                    "message": f"Found {len(data.get('records', []))} history entries",
                    "data": data,
                }

            if operation == "since":
                if not date:
                    return {"success": False, "message": "date is required for since", "data": []}
                data = await client.get_history_since(date)
                return {"success": True, "message": f"Found {len(data)} entries since {date}", "data": data}

            if operation == "by_indexer":
                if not indexer_id:
                    return {"success": False, "message": "indexer_id is required for by_indexer", "data": []}
                data = await client.get_indexer_history(indexer_id, limit=limit)
                return {"success": True, "message": f"Found {len(data)} entries for indexer {indexer_id}", "data": data}

            return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            logger.exception("prowlarr_history failed: %s", e)
            return {"success": False, "message": str(e), "data": []}
