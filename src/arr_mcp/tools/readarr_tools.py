"""Readarr portmanteau tools — author & book management."""

from __future__ import annotations

import logging
from typing import Annotated, Literal

from pydantic import Field, StrictInt

from arr_mcp.constants import TOOL_VERSION
from arr_mcp.tools.readarr_book_mutations import register_readarr_book_mutation_tools

logger = logging.getLogger(__name__)


def register_readarr_tools(mcp, client) -> None:
    if client is None:
        logger.info("Readarr not configured — skipping tools")
        return

    @mcp.tool(
        annotations={"readOnlyHint": False, "destructiveHint": False},
        version=TOOL_VERSION,
    )
    async def readarr_authors(
        operation: Annotated[
            Literal["list", "lookup", "get", "add", "delete", "update"],
            Field(description="Operation: list all, lookup by term, get by ID, add, delete, or update."),
        ],
        term: Annotated[str | None, Field(description="Search term for lookup.")] = None,
        author_id: Annotated[int | None, Field(description="Author ID for get/delete/update.")] = None,
        foreign_author_id: Annotated[str | None, Field(description="Foreign author ID for add.")] = None,
        quality_profile_id: Annotated[int | None, Field(description="Quality profile ID for add.")] = None,
        root_folder_path: Annotated[str | None, Field(description="Root folder path for add.")] = None,
        monitored: Annotated[bool, Field(description="Monitored status for add/update.")] = True,
        delete_files: Annotated[bool, Field(description="Also delete files when deleting author.")] = False,
    ) -> dict:
        """Manage Readarr authors: list, search, add, delete, update.

        ## Return Format
        {"success": bool, "message": str, "data": [...]}

        ## Examples
        readarr_authors(operation="list")
        readarr_authors(operation="lookup", term="Brandon Sanderson")
        readarr_authors(operation="add", foreign_author_id="abc-123", quality_profile_id=1, root_folder_path="/books")
        """
        try:
            if operation == "list":
                data = await client.get_authors()
                return {"success": True, "message": f"Found {len(data)} authors", "data": data}

            if operation == "lookup":
                if not term:
                    return {"success": False, "message": "term is required for lookup", "data": []}
                data = await client.lookup_author(term)
                return {"success": True, "message": f"Found {len(data)} results for '{term}'", "data": data}

            if operation == "get":
                if not author_id:
                    return {"success": False, "message": "author_id is required for get", "data": {}}
                data = await client.get_author(author_id)
                return {"success": True, "message": f"Author {author_id}", "data": data}

            if operation == "add":
                if not foreign_author_id or not quality_profile_id or not root_folder_path:
                    return {
                        "success": False,
                        "message": "foreign_author_id, quality_profile_id, and root_folder_path are required",
                        "data": {},
                    }
                data = await client.add_author(
                    foreign_author_id=foreign_author_id,
                    quality_profile_id=quality_profile_id,
                    root_folder_path=root_folder_path,
                    monitored=monitored,
                )
                return {"success": True, "message": f"Added author '{data.get('authorName', '')}'", "data": data}

            if operation == "delete":
                if not author_id:
                    return {"success": False, "message": "author_id is required for delete", "data": {}}
                await client.delete_author(author_id, delete_files=delete_files)
                return {"success": True, "message": f"Deleted author {author_id}", "data": {}}

            if operation == "update":
                if not author_id:
                    return {"success": False, "message": "author_id is required for update", "data": {}}
                data = await client.update_author(author_id, monitored=monitored)
                return {"success": True, "message": f"Updated author {author_id}", "data": data}

            return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            logger.exception("readarr_authors failed: %s", e)
            return {"success": False, "message": str(e), "data": {}}

    @mcp.tool(
        annotations={"readOnlyHint": False, "destructiveHint": False},
        version=TOOL_VERSION,
    )
    async def readarr_books(
        operation: Annotated[
            Literal["list", "get", "lookup", "search", "set_monitored"],
            Field(description="Operation: list, get, metadata lookup, native download search, or set monitored status."),
        ],
        author_id: Annotated[int | None, Field(description="Author ID for listing books.")] = None,
        book_id: Annotated[StrictInt | None, Field(description="Exact Readarr book ID for get/search/set_monitored.")] = None,
        term: Annotated[str | None, Field(description="Search term for lookup.")] = None,
        monitored: Annotated[bool, Field(description="Monitored status for set_monitored.")] = True,
    ) -> dict:
        """Manage Readarr books: list, get, lookup, search, set monitored.

        ``lookup`` finds book metadata. ``search`` starts Readarr's native
        BookSearch for one existing book and may enqueue a matching download.
        Search uses that author's current quality profile and download settings.
        The returned command ID/status confirms submission, not a completed
        download. To search while adding, use readarr_add_book with
        search_for_new_book=true.

        ## Return Format
        {"success": bool, "message": str, "data": [...]}

        ## Examples
        readarr_books(operation="list", author_id=1)
        readarr_books(operation="lookup", term="The Way of Kings")
        readarr_books(operation="search", book_id=5)
        readarr_books(operation="set_monitored", book_id=5, monitored=False)
        """
        try:
            if operation == "list":
                data = await client.get_books(author_id=author_id)
                return {"success": True, "message": f"Found {len(data)} books", "data": data}

            if operation == "get":
                if not book_id:
                    return {"success": False, "message": "book_id is required for get", "data": {}}
                data = await client.get_book(book_id)
                return {"success": True, "message": f"Book {book_id}", "data": data}

            if operation == "lookup":
                if not term:
                    return {"success": False, "message": "term is required for lookup", "data": []}
                data = await client.lookup_book(term)
                return {"success": True, "message": f"Found {len(data)} results for '{term}'", "data": data}

            if operation == "search":
                if isinstance(book_id, bool) or not isinstance(book_id, int) or book_id <= 0:
                    return {"success": False, "message": "A positive exact book_id is required for search", "data": {}}
                book = await client.get_book(book_id)
                if not isinstance(book, dict) or type(book.get("id")) is not int or book["id"] != book_id:
                    return {
                        "success": False,
                        "message": f"Readarr returned a mismatched book ID for requested book {book_id}; search was not started",
                        "data": {},
                    }
                command = await client.trigger_command("BookSearch", bookIds=[book_id])
                return {
                    "success": True,
                    "message": f"Submitted Readarr search for '{book.get('title', book_id)}' (book {book_id})",
                    "data": command,
                }

            if operation == "set_monitored":
                if not book_id:
                    return {"success": False, "message": "book_id is required for set_monitored", "data": {}}
                await client.set_books_monitored([book_id], monitored)
                return {"success": True, "message": f"Book {book_id} monitored={monitored}", "data": {}}

            return {"success": False, "message": f"Unknown operation: {operation}", "data": {}}

        except Exception as e:
            logger.exception("readarr_books failed: %s", e)
            return {"success": False, "message": str(e), "data": {}}

    register_readarr_book_mutation_tools(mcp, client)
