"""Focused Readarr book add/delete tools with conservative mutation guards."""

from __future__ import annotations

import logging
from typing import Annotated, Any, Literal

from pydantic import Field, StrictInt

from arr_mcp.constants import TOOL_VERSION

logger = logging.getLogger(__name__)

MAX_BULK_BOOK_IDS = 100
MONITOR_MODES = ("specific_book", "all", "future", "missing", "existing", "first", "latest", "none")
MONITOR_NEW_BOOK_MODES = ("all", "none", "new")
MonitorMode = Literal["specific_book", "all", "future", "missing", "existing", "first", "latest", "none"]
MonitorNewBooksMode = Literal["all", "none", "new"]


def _positive_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _failure(message: str, data: Any = None) -> dict[str, Any]:
    return {"success": False, "message": message, "data": {} if data is None else data}


def _unwrap_author(author: Any) -> dict[str, Any]:
    if not isinstance(author, dict):
        return {}
    value = author.get("value")
    return value if isinstance(value, dict) else author


def _foreign_author_id(book: dict[str, Any]) -> str | None:
    author = _unwrap_author(book.get("author"))
    value = book.get("foreignAuthorId") or author.get("foreignAuthorId")
    return value if isinstance(value, str) and value else None


def _local_author_id(book: dict[str, Any]) -> int | None:
    author = _unwrap_author(book.get("author"))
    value = book.get("authorId") or author.get("id")
    return value if _positive_int(value) else None


def _monitored_edition(book: dict[str, Any]) -> tuple[dict[str, Any] | None, str | None]:
    # /book/lookup returns the selected edition as a flattened foreignEditionId
    # on current Readarr versions. Synthesize the minimal edition object that
    # the add endpoint needs; requiring an `editions` array rejects valid live
    # lookup responses.
    foreign_edition_id = book.get("foreignEditionId")
    if isinstance(foreign_edition_id, str) and foreign_edition_id:
        return {"foreignEditionId": foreign_edition_id, "monitored": True}, None

    editions = book.get("editions")
    if not isinstance(editions, list):
        return None, "exact Readarr lookup result has no foreign edition identity; refusing add"
    monitored_editions = [
        edition
        for edition in editions
        if isinstance(edition, dict) and edition.get("monitored") is True
    ]
    if not monitored_editions:
        return None, "exact Readarr lookup result has no monitored edition; refusing add"
    if len(monitored_editions) > 1:
        return None, "exact Readarr lookup result has multiple monitored editions; refusing ambiguous add"
    return monitored_editions[0], None


async def _author_info(client: Any, book: dict[str, Any]) -> dict[str, Any]:
    author = _unwrap_author(book.get("author"))
    info = {
        "id": book.get("authorId") or author.get("id"),
        "name": author.get("authorName") or author.get("name") or book.get("authorName"),
        "foreign_author_id": _foreign_author_id(book),
    }
    if info["name"] is None and isinstance(info["id"], int) and not isinstance(info["id"], bool):
        get_author = getattr(client, "get_author", None)
        if callable(get_author):
            fetched_author = await get_author(info["id"])
            if isinstance(fetched_author, dict):
                info["name"] = fetched_author.get("authorName") or fetched_author.get("name")
                info["foreign_author_id"] = info["foreign_author_id"] or fetched_author.get("foreignAuthorId")
    return info


async def _get_book_files(client: Any, book_id: int) -> list[dict[str, Any]]:
    get_book_files = getattr(client, "get_book_files", None)
    if not callable(get_book_files):
        return []
    files = await get_book_files(book_id=book_id)
    return files if isinstance(files, list) else []


async def _preview_book(
    client: Any,
    book_id: int,
    delete_files: bool,
    confirm_delete_files: bool,
    dry_run: bool,
) -> dict[str, Any]:
    book = await client.get_book(book_id)
    if not isinstance(book, dict):
        raise TypeError(f"Readarr book {book_id} did not return an object")
    if not _positive_int(book.get("id")) or book["id"] != book_id:
        raise ValueError(f"Readarr preflight returned book ID {book.get('id')!r} for requested ID {book_id}")

    files = await _get_book_files(client, book_id)
    paths = [file.get("path") for file in files if isinstance(file, dict) and file.get("path")]
    statistics = book.get("statistics")
    reported_file_count = statistics.get("bookFileCount") if isinstance(statistics, dict) else None
    file_implications = {
        "count": len(files),
        "reported_count": reported_file_count,
        "paths": paths,
        "delete_files_requested": delete_files,
        "confirm_delete_files": confirm_delete_files,
        "would_delete_files": delete_files and confirm_delete_files,
        "will_delete_files": not dry_run and delete_files and confirm_delete_files,
    }
    return {
        "id": book_id,
        "title": book.get("title", ""),
        "author": await _author_info(client, book),
        "file_implications": file_implications,
    }


async def _find_duplicate(client: Any, foreign_book_id: str) -> dict[str, Any] | None:
    try:
        books = await client.get_books(include_all_author_books=True)
    except TypeError:
        # Keep lightweight test doubles and older client shims usable.
        books = await client.get_books()
    return next(
        (
            book
            for book in books
            if isinstance(book, dict) and book.get("foreignBookId") == foreign_book_id
        ),
        None,
    )


def _author_payload(author: dict[str, Any], *, monitored: bool) -> dict[str, Any] | None:
    foreign_id = author.get("foreignAuthorId")
    quality_profile_id = author.get("qualityProfileId")
    metadata_profile_id = author.get("metadataProfileId")
    root_folder_path = author.get("rootFolderPath") or author.get("path")
    if not isinstance(foreign_id, str) or not foreign_id:
        return None
    if not _positive_int(quality_profile_id):
        return None
    if not _positive_int(metadata_profile_id):
        return None
    if not isinstance(root_folder_path, str) or not root_folder_path.strip():
        return None

    # Keep the upstream author object intact. In particular, adding a book to
    # an existing author must not rewrite its monitoring, tags, or paths based
    # on the new-author controls exposed by this tool.
    payload: dict[str, Any] = dict(author)
    payload["foreignAuthorId"] = foreign_id
    payload["qualityProfileId"] = quality_profile_id
    payload["metadataProfileId"] = metadata_profile_id
    payload.setdefault("rootFolderPath", root_folder_path)
    payload.setdefault("monitored", monitored)
    return payload


def _new_author_payload(
    foreign_author_id: str,
    quality_profile_id: int,
    metadata_profile_id: int,
    root_folder_path: str,
    foreign_book_id: str,
    monitor: MonitorMode,
    monitor_new_books: MonitorNewBooksMode,
    tags: list[int],
) -> dict[str, Any]:
    if monitor == "specific_book":
        add_options: dict[str, Any] = {
            "monitor": "all",
            "booksToMonitor": [foreign_book_id],
        }
        author_monitored = True
    elif monitor == "none":
        add_options = {"monitor": "none", "booksToMonitor": []}
        author_monitored = False
    else:
        # Catalogue modes tell Readarr how to choose books; an explicit
        # booksToMonitor list would override that mode, so omit it.
        add_options = {"monitor": monitor}
        author_monitored = True

    add_options.update(
        {
            "searchForMissingBooks": False,
        }
    )
    return {
        "foreignAuthorId": foreign_author_id,
        "qualityProfileId": quality_profile_id,
        "metadataProfileId": metadata_profile_id,
        "rootFolderPath": root_folder_path,
        "monitored": author_monitored,
        "monitorNewItems": monitor_new_books,
        "tags": tags,
        "addOptions": add_options,
    }


async def _select_lookup_book(
    client: Any,
    foreign_book_id: str,
    *,
    require_foreign_author: bool,
) -> tuple[dict[str, Any] | None, str | None]:
    """Resolve one exact book, enriching incomplete lookup data when needed."""
    selected = await client.lookup_book(f"work:{foreign_book_id}")
    matches = [
        result
        for result in selected
        if isinstance(result, dict) and result.get("foreignBookId") == foreign_book_id
    ]
    if not matches:
        return None, f"No exact Readarr lookup result for foreign_book_id '{foreign_book_id}'"
    if len(matches) > 1:
        return (
            None,
            f"Ambiguous Readarr lookup for foreign_book_id '{foreign_book_id}'; refusing arbitrary selection",
        )

    selected_book = matches[0]
    has_identity = _foreign_author_id(selected_book) is not None or _local_author_id(selected_book) is not None
    needs_enrichment = not has_identity or (require_foreign_author and _foreign_author_id(selected_book) is None)
    if not needs_enrichment:
        return selected_book, None

    search = getattr(client, "search", None)
    if not callable(search):
        return None, "Readarr lookup result is missing author identity and search enrichment is unavailable"
    search_results = await search(f"work:{foreign_book_id}")
    enriched = [
        result.get("book")
        for result in search_results
        if isinstance(result, dict)
        and isinstance(result.get("book"), dict)
        and result["book"].get("foreignBookId") == foreign_book_id
    ]
    if not enriched:
        return None, f"No exact Readarr search result for foreign_book_id '{foreign_book_id}'"
    if len(enriched) > 1:
        return (
            None,
            f"Ambiguous Readarr search for foreign_book_id '{foreign_book_id}'; refusing arbitrary selection",
        )
    return enriched[0], None


def _unique_positive_ids(book_ids: list[int]) -> tuple[list[int], str | None]:
    unique_ids = list(dict.fromkeys(book_ids))
    if not unique_ids:
        return [], "book_ids must contain at least one positive book ID"
    if any(isinstance(book_id, bool) or not isinstance(book_id, int) or book_id <= 0 for book_id in unique_ids):
        return [], "book_ids must contain only positive exact Readarr book IDs"
    if len(unique_ids) > MAX_BULK_BOOK_IDS:
        return [], f"bulk deletion is limited to {MAX_BULK_BOOK_IDS} unique book IDs"
    return unique_ids, None


def _delete_guard(delete_files: bool, confirm_delete_files: bool) -> str | None:
    if delete_files and not confirm_delete_files:
        return "confirm_delete_files=true is required when delete_files=true"
    return None


def register_readarr_book_mutation_tools(mcp, client) -> None:
    """Register Readarr book mutations on the already-configured client."""

    @mcp.tool(
        annotations={"readOnlyHint": False, "destructiveHint": True},
        version=TOOL_VERSION,
    )
    async def readarr_add_book(
        foreign_book_id: Annotated[str, Field(description="Exact Readarr foreign book ID.")],
        author_id: Annotated[int | None, Field(gt=0, description="Existing Readarr author ID.")] = None,
        foreign_author_id: Annotated[str | None, Field(description="Foreign author ID for a new author.")] = None,
        quality_profile_id: Annotated[int | None, Field(gt=0, description="Quality profile for a new author.")] = None,
        metadata_profile_id: Annotated[
            int | None, Field(gt=0, description="Metadata profile for a new author.")
        ] = None,
        root_folder_path: Annotated[str | None, Field(description="Root folder path for a new author.")] = None,
        monitor: Annotated[
            MonitorMode,
            Field(
                description=(
                    "New-author monitoring mode: specific_book, all, future, missing, existing, first, latest, or none."
                )
            ),
        ] = "specific_book",
        monitor_new_books: Annotated[
            MonitorNewBooksMode,
            Field(description="New-author monitoring for future books: all, none, or new."),
        ] = "none",
        tags: Annotated[
            list[StrictInt], Field(description="Existing Readarr tag IDs for a new author.")
        ] = [],  # noqa: B006 - the list is read-only and MCP supplies fresh arguments
        # Retained as compatibility aliases for callers of the earlier tool
        # contract. New callers should use monitor/monitor_new_books.
        monitored: Annotated[bool, Field(description="Whether the requested book is monitored.")] = True,
        search_for_new_book: Annotated[
            bool, Field(description="Set true to start Readarr's native download search immediately after adding this book. Defaults false.")
        ] = False,
    ) -> dict[str, Any]:
        """Add exactly one Readarr book using an exact lookup edition.

        Use an existing ``author_id`` to reuse its configuration, or provide
        all four new-author fields. New-author monitoring controls map to
        Readarr's author add options; existing authors retain their settings.
        Set ``search_for_new_book=true`` to add and immediately search using
        Readarr's native addOptions.searchForNewBook. A matching release may
        be downloaded using the author's quality profile. This does not enable
        searching the author's other books.
        """
        try:
            if not isinstance(foreign_book_id, str) or not foreign_book_id.strip():
                return _failure("foreign_book_id is required")
            if monitor not in MONITOR_MODES:
                return _failure(f"monitor must be one of: {', '.join(MONITOR_MODES)}")
            if monitor_new_books not in MONITOR_NEW_BOOK_MODES:
                return _failure(
                    f"monitor_new_books must be one of: {', '.join(MONITOR_NEW_BOOK_MODES)}"
                )
            if not isinstance(tags, list) or any(not _positive_int(tag) for tag in tags):
                return _failure("tags must contain only positive exact Readarr tag IDs")
            if author_id is not None and not _positive_int(author_id):
                return _failure("author_id must be a positive exact Readarr author ID")
            new_author_fields = (foreign_author_id, quality_profile_id, metadata_profile_id, root_folder_path)
            if author_id is not None:
                if any(field is not None for field in new_author_fields):
                    return _failure("provide either author_id or the complete new-author configuration, not both")
                if monitor != "specific_book" or monitor_new_books != "none" or tags or not monitored:
                    return _failure("new-author monitoring, tags, and profile settings cannot be used with author_id")
            if author_id is None and (
                not isinstance(foreign_author_id, str)
                or not foreign_author_id.strip()
                or not _positive_int(quality_profile_id)
                or not _positive_int(metadata_profile_id)
                or not isinstance(root_folder_path, str)
                or not root_folder_path.strip()
            ):
                return _failure(
                    "author_id or foreign_author_id, quality_profile_id, metadata_profile_id, and root_folder_path are required"
                )

            # Preserve the old monitored=False call shape while making the
            # public default explicit as monitor="specific_book".
            if author_id is None and monitor == "specific_book" and not monitored:
                monitor = "none"

            duplicate = await _find_duplicate(client, foreign_book_id)
            if duplicate is not None:
                return _failure(
                    f"Book with foreign_book_id '{foreign_book_id}' is already present in Readarr",
                    {"existing": duplicate},
                )

            selected_book, lookup_error = await _select_lookup_book(
                client,
                foreign_book_id,
                require_foreign_author=author_id is None,
            )
            if lookup_error:
                return _failure(lookup_error, {"foreign_book_id": foreign_book_id})
            if selected_book is None:
                return _failure(f"No exact Readarr lookup result for foreign_book_id '{foreign_book_id}'")
            selected_edition, edition_error = _monitored_edition(selected_book)
            if edition_error:
                return _failure(edition_error, {"selected_book": selected_book})
            selected_author_id = _foreign_author_id(selected_book)
            selected_local_author_id = _local_author_id(selected_book)
            if selected_author_id is None and selected_local_author_id is None:
                return _failure(
                    "exact Readarr lookup result is missing author identity; refusing unverifiable add",
                    {"selected_book": selected_book},
                )

            if author_id is not None:
                existing_author = await client.get_author(author_id)
                author = _author_payload(existing_author, monitored=monitored)
                if author is None:
                    return _failure("existing author is missing Readarr's required nested author configuration")
                existing_local_author_id = existing_author.get("id")
                if selected_author_id and author["foreignAuthorId"] != selected_author_id:
                    return _failure(
                        "selected book belongs to a different author than author_id; refusing to add it",
                        {"selected_book": selected_book, "author": existing_author},
                    )
                if selected_local_author_id and existing_local_author_id != selected_local_author_id:
                    return _failure(
                        "selected book author ID does not match author_id; refusing to add it",
                        {"selected_book": selected_book, "author": existing_author},
                    )
            else:
                if selected_author_id is None:
                    return _failure(
                        "exact Readarr lookup result is missing foreign author identity for a new author",
                        {"selected_book": selected_book},
                    )
                if foreign_author_id != selected_author_id:
                    return _failure(
                        "foreign_author_id does not match the selected book's author",
                        {"selected_book": selected_book},
                    )
                author = _new_author_payload(
                    foreign_author_id=foreign_author_id,  # type: ignore[arg-type]
                    quality_profile_id=quality_profile_id,  # type: ignore[arg-type]
                    metadata_profile_id=metadata_profile_id,  # type: ignore[arg-type]
                    root_folder_path=root_folder_path,  # type: ignore[arg-type]
                    foreign_book_id=foreign_book_id,
                    monitor=monitor,
                    monitor_new_books=monitor_new_books,
                    tags=tags,
                )

            data = await client.add_book(
                foreign_book_id=foreign_book_id,
                author=author,
                monitored=(monitor != "none") if author_id is None else monitored,
                search_for_new_book=search_for_new_book,
                editions=[selected_edition],
            )
            return {"success": True, "message": f"Added Readarr book '{selected_book.get('title', foreign_book_id)}'", "data": data}
        except Exception as exc:
            logger.exception("readarr_add_book failed: %s", exc)
            return _failure(str(exc))

    @mcp.tool(
        annotations={"readOnlyHint": False, "destructiveHint": True},
        version=TOOL_VERSION,
    )
    async def readarr_delete_book(
        book_id: Annotated[StrictInt, Field(gt=0, description="Positive exact Readarr book ID.")],
        dry_run: Annotated[bool, Field(description="Preview the book and files without deleting. Defaults true.")] = True,
        delete_files: Annotated[bool, Field(description="Also delete files from disk.")] = False,
        confirm_delete_files: Annotated[
            bool, Field(description="Required confirmation when delete_files=true.")
        ] = False,
        add_import_list_exclusion: Annotated[
            bool, Field(description="Add an import-list exclusion for this book.")
        ] = False,
    ) -> dict[str, Any]:
        """Preview or delete one Readarr book; never deletes its author."""
        try:
            if not _positive_int(book_id):
                return _failure("book_id must be a positive exact Readarr book ID")
            guard_error = _delete_guard(delete_files, confirm_delete_files)
            if guard_error and not dry_run:
                return _failure(guard_error)
            preview = await _preview_book(client, book_id, delete_files, confirm_delete_files, dry_run)
            if dry_run:
                return {
                    "success": True,
                    "message": f"Dry run: Readarr book {book_id} was not deleted",
                    "data": {"dry_run": True, "preview": preview},
                }
            result = await client.delete_book(
                book_id,
                delete_files=delete_files,
                add_import_list_exclusion=add_import_list_exclusion,
            )
            return {
                "success": True,
                "message": f"Deleted Readarr book {book_id}; author was retained",
                "data": {"dry_run": False, "preview": preview, "result": result},
            }
        except Exception as exc:
            logger.exception("readarr_delete_book failed: %s", exc)
            return _failure(str(exc))

    @mcp.tool(
        annotations={"readOnlyHint": False, "destructiveHint": True},
        version=TOOL_VERSION,
    )
    async def readarr_delete_books(
        book_ids: Annotated[
            list[StrictInt], Field(description="Positive exact Readarr book IDs; duplicates are removed.")
        ],
        dry_run: Annotated[bool, Field(description="Preview all books without deleting. Defaults true.")] = True,
        delete_files: Annotated[bool, Field(description="Also delete files from disk.")] = False,
        confirm_delete_files: Annotated[
            bool, Field(description="Required confirmation when delete_files=true.")
        ] = False,
        add_import_list_exclusion: Annotated[
            bool, Field(description="Add import-list exclusions for deleted books.")
        ] = False,
    ) -> dict[str, Any]:
        """Preview or sequentially delete up to 100 unique Readarr books.

        Every ID is preflighted before the first mutation. A later delete
        failure stops the sequence and reports IDs that were not attempted.
        """
        try:
            if not isinstance(book_ids, list):
                return _failure("book_ids must be a list of positive exact Readarr book IDs")
            unique_ids, validation_error = _unique_positive_ids(book_ids)
            if validation_error:
                return _failure(validation_error)
            guard_error = _delete_guard(delete_files, confirm_delete_files)
            if guard_error and not dry_run:
                return _failure(guard_error)

            previews: list[dict[str, Any]] = []
            preflight_errors: list[dict[str, Any]] = []
            for current_id in unique_ids:
                try:
                    previews.append(
                        await _preview_book(client, current_id, delete_files, confirm_delete_files, dry_run)
                    )
                except Exception as exc:
                    preflight_errors.append({"id": current_id, "error": str(exc)})

            base_data = {
                "requested_ids": unique_ids,
                "previews": previews,
                "preflight_errors": preflight_errors,
                "deleted": [],
                "failed": [],
                "not_attempted": unique_ids,
            }
            if preflight_errors:
                return _failure("Bulk deletion preflight failed; no books were deleted", base_data)
            if dry_run:
                base_data["dry_run"] = True
                return {"success": True, "message": "Bulk dry run: no Readarr books were deleted", "data": base_data}

            deleted: list[dict[str, Any]] = []
            for index, (current_id, preview) in enumerate(zip(unique_ids, previews, strict=True)):
                try:
                    result = await client.delete_book(
                        current_id,
                        delete_files=delete_files,
                        add_import_list_exclusion=add_import_list_exclusion,
                    )
                    deleted.append({"id": current_id, "title": preview.get("title", ""), "result": result})
                except Exception as exc:
                    base_data["deleted"] = deleted
                    base_data["failed"] = [{"id": current_id, "error": str(exc)}]
                    base_data["not_attempted"] = unique_ids[index + 1 :]
                    return _failure(
                        f"Bulk deletion stopped after Readarr book {current_id} failed; later IDs were not attempted",
                        base_data,
                    )

            base_data["deleted"] = deleted
            base_data["not_attempted"] = []
            return {
                "success": True,
                "message": f"Deleted {len(deleted)} Readarr books sequentially; authors were retained",
                "data": {**base_data, "dry_run": False},
            }
        except Exception as exc:
            logger.exception("readarr_delete_books failed: %s", exc)
            return _failure(str(exc))
