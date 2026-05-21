"""Overseerr portmanteau tool — media requests & discovery management."""

from __future__ import annotations

import logging
from typing import Annotated, Literal

from pydantic import Field

logger = logging.getLogger(__name__)


def register_overseerr_tools(mcp, client) -> None:
    if client is None:
        logger.info("Overseerr not configured — skipping tools")
        return

    @mcp.tool(
        annotations={"readOnlyHint": False, "destructiveHint": False},
        version="0.1.0",
    )
    async def overseerr_requests(
        operation: Annotated[
            Literal["list", "get", "create", "approve", "decline", "delete", "count", "pending"],
            Field(
                description="Operation: list all, get by ID, create, approve, decline, delete, count, or view pending."
            ),
        ],
        request_id: Annotated[int | None, Field(description="Request ID for get/approve/decline/delete.")] = None,
        media_type: Annotated[str | None, Field(description="Media type: 'movie' or 'tv' for create.")] = None,
        media_id: Annotated[int | None, Field(description="TMDB ID for create.")] = None,
        tvdb_id: Annotated[int | None, Field(description="TVDB ID for TV requests.")] = None,
        seasons: Annotated[list[int] | None, Field(description="Season numbers for TV requests.")] = None,
        is4k: Annotated[bool, Field(description="Request 4K quality.")] = False,
        request_filter: Annotated[
            str, Field(description="Filter: 'all', 'approved', 'available', 'pending', 'processing', 'failed'.")
        ] = "all",
        take: Annotated[int, Field(description="Results per page.")] = 20,
        skip: Annotated[int, Field(description="Offset for pagination.")] = 0,
    ) -> dict:
        """Manage Overseerr media requests: view, create, approve, decline, delete.

        Overseerr is the user-facing request gateway for the *arr stack.
        Users request movies/TV shows through Overseerr, which routes to
        Radarr/Sonarr for fulfillment.

        ## Return Format
        {"success": bool, "message": str, "data": [...]}

        ## Examples
        overseerr_requests(operation="list", filter="pending")
        overseerr_requests(operation="create", media_type="movie", media_id=438631)
        overseerr_requests(operation="approve", request_id=42)
        overseerr_requests(operation="count")
        """
        try:
            if operation == "list":
                data = await client.get_requests(take=take, skip=skip, request_filter=request_filter)
                return {"success": True, "message": f"Found {len(data.get('results', []))} requests", "data": data}

            if operation == "pending":
                data = await client.get_requests(take=take, skip=skip, request_filter="pending")
                return {
                    "success": True,
                    "message": f"Found {len(data.get('results', []))} pending requests",
                    "data": data,
                }

            if operation == "get":
                if not request_id:
                    return {"success": False, "message": "request_id is required for get", "data": {}}
                data = await client.get_request(request_id)
                return {"success": True, "message": f"Request {request_id}", "data": data}

            if operation == "create":
                if not media_type or not media_id:
                    return {"success": False, "message": "media_type and media_id are required", "data": {}}
                data = await client.create_request(
                    media_type=media_type,
                    media_id=media_id,
                    tvdb_id=tvdb_id,
                    seasons=seasons,
                    is4k=is4k,
                )
                return {"success": True, "message": f"Created {media_type} request {media_id}", "data": data}

            if operation == "approve":
                if not request_id:
                    return {"success": False, "message": "request_id is required for approve", "data": {}}
                data = await client.approve_request(request_id)
                return {"success": True, "message": f"Approved request {request_id}", "data": data}

            if operation == "decline":
                if not request_id:
                    return {"success": False, "message": "request_id is required for decline", "data": {}}
                data = await client.decline_request(request_id)
                return {"success": True, "message": f"Declined request {request_id}", "data": data}

            if operation == "delete":
                if not request_id:
                    return {"success": False, "message": "request_id is required for delete", "data": {}}
                await client.delete_request(request_id)
                return {"success": True, "message": f"Deleted request {request_id}", "data": {}}

            if operation == "count":
                data = await client.get_request_count()
                return {"success": True, "message": "Request counts", "data": data}

            return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            logger.exception("overseerr_requests failed: %s", e)
            return {"success": False, "message": str(e), "data": {}}

    @mcp.tool(
        annotations={"readOnlyHint": True, "destructiveHint": False},
        version="0.1.0",
    )
    async def overseerr_search(
        query: Annotated[str, Field(description="Search query for movies, TV shows, and people.")],
        page: Annotated[int, Field(description="Page number.")] = 1,
    ) -> dict:
        """Search Overseerr for movies, TV shows, and people across TMDB.

        ## Return Format
        {"success": bool, "message": str, "data": {results: [...]}}

        ## Examples
        overseerr_search(query="Dune")
        overseerr_search(query="The Expanse")
        """
        try:
            data = await client.search(query, page=page)
            total = len(data.get("results", []))
            return {"success": True, "message": f"Found {total} results for '{query}'", "data": data}
        except Exception as e:
            logger.exception("overseerr_search failed: %s", e)
            return {"success": False, "message": str(e), "data": {}}

    @mcp.tool(
        annotations={"readOnlyHint": True, "destructiveHint": False},
        version="0.1.0",
    )
    async def overseerr_users(
        operation: Annotated[
            Literal["list", "get", "requests"],
            Field(description="Operation: list users, get by ID, or view user's requests."),
        ],
        user_id: Annotated[int | None, Field(description="User ID for get/requests.")] = None,
        take: Annotated[int, Field(description="Results per page.")] = 20,
    ) -> dict:
        """Manage Overseerr users and their request history.

        ## Return Format
        {"success": bool, "message": str, "data": [...]}

        ## Examples
        overseerr_users(operation="list")
        overseerr_users(operation="requests", user_id=1)
        """
        try:
            if operation == "list":
                data = await client.get_users(take=take)
                return {"success": True, "message": f"Found {len(data.get('results', []))} users", "data": data}

            if operation == "get":
                if not user_id:
                    return {"success": False, "message": "user_id is required for get", "data": {}}
                data = await client.get_user(user_id)
                return {"success": True, "message": f"User {user_id}", "data": data}

            if operation == "requests":
                if not user_id:
                    return {"success": False, "message": "user_id is required for requests", "data": {}}
                data = await client.get_user_requests(user_id, take=take)
                return {"success": True, "message": f"Found requests for user {user_id}", "data": data}

            return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            logger.exception("overseerr_users failed: %s", e)
            return {"success": False, "message": str(e), "data": {}}
