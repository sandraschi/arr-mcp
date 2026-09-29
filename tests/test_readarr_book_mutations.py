"""Independent regression tests for Readarr book mutation MCP tools.

All requests are intercepted by pytest-httpx.  These tests deliberately use the
real Readarr client under the registered tools so validation and HTTP payloads
are checked together without touching a Readarr instance.
"""

from __future__ import annotations

import inspect
import json
from collections.abc import Callable
from typing import Any
from urllib.parse import parse_qs

import httpx
import pytest
import pytest_asyncio

from arr_mcp.constants import TOOL_VERSION
from arr_mcp.services.readarr_service import ReadarrClient
from arr_mcp.tools.readarr_tools import register_readarr_tools

READARR_URL = "http://localhost:8787/readarr"
API_ROOT = "/readarr/api/v1"
API_KEY = "test-api-key"


class RecordingMCP:
    """Small MCP stand-in that retains registration metadata for assertions."""

    def __init__(self) -> None:
        self.tools: dict[str, Callable[..., Any]] = {}
        self.options: dict[str, dict[str, Any]] = {}

    def tool(self, **kwargs: Any):
        def decorator(fn: Callable[..., Any]):
            self.tools[fn.__name__] = fn
            self.options[fn.__name__] = kwargs
            return fn

        return decorator


@pytest_asyncio.fixture
async def readarr():
    client = ReadarrClient(READARR_URL, API_KEY)
    yield client
    await client.close()


def _author(author_id: int = 7, foreign_author_id: str = "author-7") -> dict[str, Any]:
    return {
        "id": author_id,
        "authorName": "Example Author",
        "foreignAuthorId": foreign_author_id,
        "qualityProfileId": 2,
        "metadataProfileId": 3,
        "path": "/books/example-author",
        "monitored": True,
    }


def _book(book_id: int, foreign_book_id: str, author_id: int = 7, title: str | None = None) -> dict[str, Any]:
    return {
        "id": book_id,
        "title": title or f"Book {book_id}",
        "foreignBookId": foreign_book_id,
        "authorId": author_id,
        "author": _author(author_id),
        "monitored": True,
        "statistics": {"bookFileCount": 1, "sizeOnDisk": 1234},
    }


def _mock_readarr(
    httpx_mock,
    *,
    books: list[dict[str, Any]] | None = None,
    authors: list[dict[str, Any]] | None = None,
    lookup_books: list[dict[str, Any]] | None = None,
    search_results: list[dict[str, Any]] | None = None,
    delete_failures: set[int] | None = None,
    book_response_overrides: dict[int, dict[str, Any]] | None = None,
) -> list[httpx.Request]:
    """Install a narrow in-memory Readarr API and return every intercepted request."""

    books = books or []
    authors = authors or []
    lookup_books = lookup_books or []
    search_results = search_results or []
    delete_failures = delete_failures or set()
    book_response_overrides = book_response_overrides or {}
    requests: list[httpx.Request] = []
    next_book_id = max((int(book.get("id", 0)) for book in books), default=40) + 1

    def callback(request: httpx.Request) -> httpx.Response:
        nonlocal next_book_id
        requests.append(request)
        path = request.url.path

        if request.method == "GET" and path == f"{API_ROOT}/book":
            return httpx.Response(200, json=books)

        if request.method == "GET" and path == f"{API_ROOT}/book/lookup":
            return httpx.Response(200, json=lookup_books)

        if request.method == "GET" and path == f"{API_ROOT}/search":
            return httpx.Response(200, json=search_results)

        if request.method == "GET" and path == f"{API_ROOT}/bookfile":
            return httpx.Response(200, json=[])

        if request.method == "GET" and path.startswith(f"{API_ROOT}/book/"):
            book_id = int(path.rsplit("/", 1)[-1])
            if book_id in book_response_overrides:
                return httpx.Response(200, json=book_response_overrides[book_id])
            matching = next((book for book in books if book.get("id") == book_id), None)
            if matching is None:
                return httpx.Response(404, json={"message": "book not found"})
            return httpx.Response(200, json=matching)

        if request.method == "GET" and path == f"{API_ROOT}/author":
            return httpx.Response(200, json=authors)

        if request.method == "GET" and path.startswith(f"{API_ROOT}/author/"):
            author_id = int(path.rsplit("/", 1)[-1])
            matching = next((author for author in authors if author.get("id") == author_id), None)
            if matching is None:
                return httpx.Response(404, json={"message": "author not found"})
            return httpx.Response(200, json=matching)

        if request.method == "POST" and path == f"{API_ROOT}/book":
            payload = json.loads(request.content)
            response = {"id": next_book_id, **payload}
            next_book_id += 1
            return httpx.Response(201, json=response)

        if request.method == "DELETE" and path.startswith(f"{API_ROOT}/book/"):
            book_id = int(path.rsplit("/", 1)[-1])
            if book_id in delete_failures:
                return httpx.Response(500, json={"message": "delete failed"})
            return httpx.Response(204)

        raise AssertionError(f"unexpected mocked Readarr request: {request.method} {request.url}")

    httpx_mock.add_callback(callback, is_reusable=True, is_optional=True)
    return requests


def _tools(client: ReadarrClient) -> tuple[RecordingMCP, dict[str, Callable[..., Any]]]:
    mcp = RecordingMCP()
    register_readarr_tools(mcp, client)
    return mcp, mcp.tools


def _requests(requests: list[httpx.Request], method: str, path: str | None = None) -> list[httpx.Request]:
    return [
        request
        for request in requests
        if request.method == method and (path is None or request.url.path == path)
    ]


class TestReadarrBookMutationRegistration:
    def test_registers_distinct_tools_with_mutation_annotations(self):
        mcp, _ = _tools(object())  # type: ignore[arg-type]

        expected = {"readarr_add_book", "readarr_delete_book", "readarr_delete_books"}
        assert expected <= mcp.tools.keys()
        assert mcp.options["readarr_add_book"]["version"] == TOOL_VERSION
        assert mcp.options["readarr_delete_book"]["version"] == TOOL_VERSION
        assert mcp.options["readarr_delete_books"]["version"] == TOOL_VERSION
        assert mcp.options["readarr_add_book"]["annotations"] == {
            "readOnlyHint": False,
            "destructiveHint": True,
        }
        for name in ("readarr_delete_book", "readarr_delete_books"):
            assert mcp.options[name]["annotations"] == {
                "readOnlyHint": False,
                "destructiveHint": True,
            }

    def test_public_signatures_keep_safe_defaults_and_exact_id_inputs(self):
        mcp, tools = _tools(object())  # type: ignore[arg-type]

        add_parameters = inspect.signature(tools["readarr_add_book"]).parameters
        assert list(add_parameters)[:6] == [
            "foreign_book_id",
            "author_id",
            "foreign_author_id",
            "quality_profile_id",
            "metadata_profile_id",
            "root_folder_path",
        ]
        assert {"monitored", "search_for_new_book"} <= add_parameters.keys()
        assert add_parameters["search_for_new_book"].default is False
        assert {"monitor", "monitor_new_books", "tags"} <= add_parameters.keys()
        assert add_parameters["monitor"].default == "specific_book"
        assert add_parameters["monitor_new_books"].default == "none"

        for name in ("readarr_delete_book", "readarr_delete_books"):
            parameters = inspect.signature(tools[name]).parameters
            assert parameters["dry_run"].default is True
            assert parameters["delete_files"].default is False
            assert parameters["confirm_delete_files"].default is False
            assert parameters["add_import_list_exclusion"].default is False


class TestReadarrAddBookTool:
    @pytest.mark.asyncio
    async def test_existing_author_reuses_configuration_and_limits_monitoring_to_selected_book(
        self, readarr, httpx_mock
    ):
        author = _author()
        requests = _mock_readarr(
            httpx_mock,
            authors=[author],
            books=[],
            lookup_books=[
                {
                    "foreignBookId": "book-123",
                    "foreignEditionId": "edition-123",
                    "authorId": 7,
                    "title": "Selected Book",
                    "author": {"foreignAuthorId": "author-7"},
                }
            ],
        )
        _, tools = _tools(readarr)

        result = await tools["readarr_add_book"](
            foreign_book_id="book-123",
            author_id=7,
        )

        assert result["success"] is True
        posts = _requests(requests, "POST", f"{API_ROOT}/book")
        assert len(posts) == 1
        payload = json.loads(posts[0].content)
        assert payload["foreignBookId"] == "book-123"
        assert payload["author"]["id"] == 7
        assert payload["author"]["qualityProfileId"] == 2
        assert payload["author"]["metadataProfileId"] == 3
        assert payload["author"]["metadataProfileId"] == author["metadataProfileId"]
        assert payload["author"]["path"] == author["path"]
        assert payload["editions"] == [{"foreignEditionId": "edition-123", "monitored": True}]
        assert payload["addOptions"]["searchForNewBook"] is False
        assert payload["author"].get("addOptions") is None
        assert payload["author"]["monitored"] is author["monitored"]
        lookup_requests = _requests(requests, "GET", f"{API_ROOT}/book/lookup")
        assert len(lookup_requests) == 1
        assert parse_qs(lookup_requests[0].url.query.decode())["term"] == ["work:book-123"]

    @pytest.mark.asyncio
    async def test_existing_author_can_opt_into_native_book_search_without_extra_command_post(
        self, readarr, httpx_mock
    ):
        author = _author()
        requests = _mock_readarr(
            httpx_mock,
            authors=[author],
            books=[],
            lookup_books=[
                {
                    "foreignBookId": "book-123",
                    "foreignEditionId": "edition-123",
                    "authorId": 7,
                    "title": "Selected Book",
                    "author": {"foreignAuthorId": "author-7"},
                }
            ],
        )
        _, tools = _tools(readarr)

        result = await tools["readarr_add_book"](
            foreign_book_id="book-123",
            author_id=7,
            search_for_new_book=True,
        )

        assert result["success"] is True
        posts = _requests(requests, "POST", f"{API_ROOT}/book")
        assert len(posts) == 1
        assert json.loads(posts[0].content)["addOptions"] == {"searchForNewBook": True}
        assert _requests(requests, "POST", f"{API_ROOT}/command") == []

    @pytest.mark.asyncio
    async def test_new_author_defaults_to_requested_book_monitoring(self, readarr, httpx_mock):
        requests = _mock_readarr(
            httpx_mock,
            books=[],
            lookup_books=[
                {
                    "foreignBookId": "book-new",
                    "foreignEditionId": "edition-new",
                    "authorId": 8,
                    "title": "Selected New Book",
                    "author": {"foreignAuthorId": "author-new"},
                }
            ],
        )
        _, tools = _tools(readarr)

        result = await tools["readarr_add_book"](
            foreign_book_id="book-new",
            foreign_author_id="author-new",
            quality_profile_id=2,
            metadata_profile_id=3,
            root_folder_path="/books/new-author",
        )

        assert result["success"] is True
        posts = _requests(requests, "POST", f"{API_ROOT}/book")
        assert len(posts) == 1
        payload = json.loads(posts[0].content)
        assert payload["foreignBookId"] == "book-new"
        nested_author = payload["author"]
        assert nested_author["foreignAuthorId"] == "author-new"
        assert nested_author["qualityProfileId"] == 2
        assert nested_author["metadataProfileId"] == 3
        assert nested_author["rootFolderPath"] == "/books/new-author"
        assert nested_author["monitored"] is True
        assert nested_author["monitorNewItems"] == "none"
        assert nested_author["addOptions"]["monitor"] == "all"
        assert nested_author["addOptions"]["booksToMonitor"] == ["book-new"]
        assert nested_author["addOptions"]["searchForMissingBooks"] is False
        assert payload["editions"] == [{"foreignEditionId": "edition-new", "monitored": True}]
        assert payload["addOptions"]["searchForNewBook"] is False

    @pytest.mark.asyncio
    async def test_new_author_enriches_flat_lookup_with_unique_search_author(self, readarr, httpx_mock):
        requests = _mock_readarr(
            httpx_mock,
            books=[],
            lookup_books=[
                {
                    "foreignBookId": "book-enriched",
                    "foreignEditionId": "edition-enriched",
                    "authorId": 0,
                    "title": "Enriched Book",
                }
            ],
            search_results=[
                {
                    "book": {
                        "foreignBookId": "book-enriched",
                        "foreignEditionId": "edition-enriched",
                        "title": "Enriched Book",
                        "author": {"foreignAuthorId": "author-enriched"},
                    }
                }
            ],
        )
        _, tools = _tools(readarr)

        result = await tools["readarr_add_book"](
            foreign_book_id="book-enriched",
            foreign_author_id="author-enriched",
            quality_profile_id=2,
            metadata_profile_id=3,
            root_folder_path="/books/enriched",
        )

        assert result["success"] is True
        search_requests = _requests(requests, "GET", f"{API_ROOT}/search")
        assert len(search_requests) == 1
        assert parse_qs(search_requests[0].url.query.decode())["term"] == ["work:book-enriched"]
        assert len(_requests(requests, "POST", f"{API_ROOT}/book")) == 1

    @pytest.mark.asyncio
    async def test_new_author_rejects_search_result_without_foreign_author_identity(self, readarr, httpx_mock):
        requests = _mock_readarr(
            httpx_mock,
            books=[],
            lookup_books=[
                {
                    "foreignBookId": "book-no-author",
                    "foreignEditionId": "edition-no-author",
                    "authorId": 0,
                    "title": "No Author Identity",
                }
            ],
            search_results=[
                {
                    "book": {
                        "foreignBookId": "book-no-author",
                        "foreignEditionId": "edition-no-author",
                        "title": "No Author Identity",
                    }
                }
            ],
        )
        _, tools = _tools(readarr)

        result = await tools["readarr_add_book"](
            foreign_book_id="book-no-author",
            foreign_author_id="author-unknown",
            quality_profile_id=2,
            metadata_profile_id=3,
            root_folder_path="/books/no-author",
        )

        assert result["success"] is False
        assert "author" in result["message"].lower()
        assert _requests(requests, "POST", f"{API_ROOT}/book") == []

    @pytest.mark.asyncio
    async def test_explicit_new_author_monitor_and_tags_map_without_forcing_one_book(self, readarr, httpx_mock):
        requests = _mock_readarr(
            httpx_mock,
            books=[],
            lookup_books=[
                {
                    "foreignBookId": "book-catalogue",
                    "foreignEditionId": "edition-catalogue",
                    "authorId": 8,
                    "title": "Catalogue Book",
                    "author": {"foreignAuthorId": "author-catalogue"},
                }
            ],
        )
        _, tools = _tools(readarr)

        result = await tools["readarr_add_book"](
            foreign_book_id="book-catalogue",
            foreign_author_id="author-catalogue",
            quality_profile_id=2,
            metadata_profile_id=3,
            root_folder_path="/books/catalogue",
            monitor="all",
            monitor_new_books="all",
            tags=[4, 9],
        )

        assert result["success"] is True
        payload = json.loads(_requests(requests, "POST", f"{API_ROOT}/book")[0].content)
        nested_author = payload["author"]
        assert nested_author["addOptions"]["monitor"] == "all"
        assert nested_author["addOptions"].get("booksToMonitor", []) == []
        assert nested_author["monitorNewItems"] == "all"
        assert nested_author["tags"] == [4, 9]

    @pytest.mark.asyncio
    async def test_unmonitored_new_author_does_not_monitor_any_book(self, readarr, httpx_mock):
        requests = _mock_readarr(
            httpx_mock,
            books=[],
            lookup_books=[
                {
                    "foreignBookId": "book-unmonitored",
                    "foreignEditionId": "edition-unmonitored",
                    "authorId": 8,
                    "title": "Unmonitored Book",
                    "author": {"foreignAuthorId": "author-unmonitored"},
                }
            ],
        )
        _, tools = _tools(readarr)

        result = await tools["readarr_add_book"](
            foreign_book_id="book-unmonitored",
            foreign_author_id="author-unmonitored",
            quality_profile_id=2,
            metadata_profile_id=3,
            root_folder_path="/books/unmonitored",
            monitor="none",
        )

        assert result["success"] is True
        payload = json.loads(_requests(requests, "POST", f"{API_ROOT}/book")[0].content)
        assert payload["monitored"] is False
        assert payload["author"]["addOptions"]["monitor"] == "none"
        assert payload["author"]["addOptions"]["booksToMonitor"] == []

    @pytest.mark.asyncio
    async def test_duplicate_foreign_book_is_rejected_without_post(self, readarr, httpx_mock):
        requests = _mock_readarr(
            httpx_mock,
            authors=[_author()],
            books=[_book(10, "book-existing")],
        )
        _, tools = _tools(readarr)

        result = await tools["readarr_add_book"](
            foreign_book_id="book-existing",
            author_id=7,
        )

        assert result["success"] is False
        assert "duplicate" in result["message"].lower() or "already" in result["message"].lower()
        assert _requests(requests, "POST", f"{API_ROOT}/book") == []

    @pytest.mark.asyncio
    async def test_ambiguous_exact_foreign_book_lookup_is_rejected_without_post(self, readarr, httpx_mock):
        requests = _mock_readarr(
            httpx_mock,
            books=[],
            lookup_books=[
                {"foreignBookId": "book-ambiguous", "title": "Edition A"},
                {"foreignBookId": "book-ambiguous", "title": "Edition B"},
            ],
        )
        _, tools = _tools(readarr)

        result = await tools["readarr_add_book"](
            foreign_book_id="book-ambiguous",
            foreign_author_id="author-new",
            quality_profile_id=2,
            metadata_profile_id=3,
            root_folder_path="/books/new-author",
        )

        assert result["success"] is False
        assert "ambiguous" in result["message"].lower()
        assert _requests(requests, "POST", f"{API_ROOT}/book") == []

    @pytest.mark.asyncio
    async def test_selected_book_author_must_match_supplied_author(self, readarr, httpx_mock):
        requests = _mock_readarr(
            httpx_mock,
            authors=[_author(7)],
            books=[],
            lookup_books=[
                {
                    "foreignBookId": "book-selected",
                    "foreignEditionId": "edition-selected",
                    "authorId": 8,
                    "title": "Selected Book",
                }
            ],
        )
        _, tools = _tools(readarr)

        result = await tools["readarr_add_book"](
            foreign_book_id="book-selected",
            author_id=7,
        )

        assert result["success"] is False
        assert "author" in result["message"].lower()
        assert _requests(requests, "POST", f"{API_ROOT}/book") == []

    @pytest.mark.asyncio
    async def test_zero_lookup_author_id_is_enriched_before_existing_author_mismatch(self, readarr, httpx_mock):
        requests = _mock_readarr(
            httpx_mock,
            authors=[_author(7, "author-7")],
            books=[],
            lookup_books=[
                {
                    "foreignBookId": "book-zero-author",
                    "foreignEditionId": "edition-zero-author",
                    "authorId": 0,
                    "title": "Zero Author ID",
                }
            ],
            search_results=[
                {
                    "book": {
                        "foreignBookId": "book-zero-author",
                        "foreignEditionId": "edition-zero-author",
                        "author": {"foreignAuthorId": "author-8"},
                    }
                }
            ],
        )
        _, tools = _tools(readarr)

        result = await tools["readarr_add_book"](
            foreign_book_id="book-zero-author",
            author_id=7,
        )

        assert result["success"] is False
        assert "different author" in result["message"].lower()
        assert len(_requests(requests, "GET", f"{API_ROOT}/search")) == 1
        assert _requests(requests, "POST", f"{API_ROOT}/book") == []

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "kwargs",
        [
            {"foreign_book_id": ""},
            {"foreign_book_id": "book-1", "author_id": 7, "foreign_author_id": "author-new"},
            {"foreign_book_id": "book-1", "author_id": 7, "monitor": "all"},
            {"foreign_book_id": "book-1", "author_id": 7, "tags": [4]},
            {
                "foreign_book_id": "book-1",
                "foreign_author_id": "author-new",
                "quality_profile_id": 2,
                "root_folder_path": "/books",
            },
        ],
    )
    async def test_invalid_add_input_makes_no_http_write(self, readarr, httpx_mock, kwargs):
        requests = _mock_readarr(httpx_mock, books=[])
        _, tools = _tools(readarr)

        result = await tools["readarr_add_book"](**kwargs)

        assert result["success"] is False
        assert _requests(requests, "POST", f"{API_ROOT}/book") == []


class TestReadarrDeleteBookTool:
    @pytest.mark.asyncio
    async def test_individual_delete_defaults_to_preview_with_file_implication(self, readarr, httpx_mock):
        book = _book(11, "book-11", title="Preview Book")
        requests = _mock_readarr(httpx_mock, books=[book])
        _, tools = _tools(readarr)

        result = await tools["readarr_delete_book"](book_id=11)

        assert result["success"] is True
        preview = result["data"]["preview"]
        assert preview["id"] == 11
        assert preview["title"] == "Preview Book"
        assert preview["author"]["id"] == 7
        assert preview["file_implications"]["delete_files_requested"] is False
        assert preview["file_implications"]
        assert _requests(requests, "DELETE") == []

    @pytest.mark.asyncio
    async def test_delete_files_requires_separate_confirmation(self, readarr, httpx_mock):
        book = _book(11, "book-11")
        requests = _mock_readarr(httpx_mock, books=[book])
        _, tools = _tools(readarr)

        result = await tools["readarr_delete_book"](
            book_id=11,
            dry_run=False,
            delete_files=True,
        )

        assert result["success"] is False
        assert "confirm" in result["message"].lower()
        assert _requests(requests, "DELETE") == []

    @pytest.mark.asyncio
    async def test_confirmed_delete_sends_exact_positive_id_and_import_exclusion(self, readarr, httpx_mock):
        requests = _mock_readarr(httpx_mock, books=[_book(11, "book-11")])
        _, tools = _tools(readarr)

        result = await tools["readarr_delete_book"](
            book_id=11,
            dry_run=False,
            delete_files=True,
            confirm_delete_files=True,
            add_import_list_exclusion=True,
        )

        assert result["success"] is True
        deletes = _requests(requests, "DELETE", f"{API_ROOT}/book/11")
        assert len(deletes) == 1
        assert parse_qs(deletes[0].url.query.decode()) == {
            "deleteFiles": ["true"],
            "addImportListExclusion": ["true"],
        }

    @pytest.mark.asyncio
    @pytest.mark.parametrize("book_id", [0, -1, None, True, False])
    async def test_non_positive_or_missing_id_makes_no_http_write(self, readarr, httpx_mock, book_id):
        requests = _mock_readarr(httpx_mock, books=[])
        _, tools = _tools(readarr)

        result = await tools["readarr_delete_book"](book_id=book_id)

        assert result["success"] is False
        assert _requests(requests, "DELETE") == []


class TestReadarrBulkDeleteBookTool:
    @pytest.mark.asyncio
    async def test_bulk_preview_preflights_all_books_without_deleting(self, readarr, httpx_mock):
        requests = _mock_readarr(httpx_mock, books=[_book(11, "book-11"), _book(12, "book-12")])
        _, tools = _tools(readarr)

        result = await tools["readarr_delete_books"](book_ids=[11, 12])

        assert result["success"] is True
        assert {item["id"] for item in result["data"]["previews"]} == {11, 12}
        assert len(_requests(requests, "GET")) >= 2
        assert _requests(requests, "DELETE") == []

    @pytest.mark.asyncio
    async def test_bulk_preflight_rejects_missing_id_before_any_delete(self, readarr, httpx_mock):
        requests = _mock_readarr(httpx_mock, books=[_book(11, "book-11")])
        _, tools = _tools(readarr)

        result = await tools["readarr_delete_books"](
            book_ids=[11, 99],
            dry_run=False,
        )

        assert result["success"] is False
        assert _requests(requests, "DELETE") == []
        assert "99" in result["message"] or any(
            item["id"] == 99 for item in result["data"]["preflight_errors"]
        )

    @pytest.mark.asyncio
    async def test_bulk_deduplicates_ids_and_deletes_sequentially(self, readarr, httpx_mock):
        requests = _mock_readarr(
            httpx_mock,
            books=[_book(11, "book-11"), _book(12, "book-12")],
        )
        _, tools = _tools(readarr)

        result = await tools["readarr_delete_books"](
            book_ids=[11, 11, 12],
            dry_run=False,
        )

        assert result["success"] is True
        deletes = _requests(requests, "DELETE")
        assert [request.url.path for request in deletes] == [f"{API_ROOT}/book/11", f"{API_ROOT}/book/12"]
        assert all(parse_qs(request.url.query.decode())["deleteFiles"] == ["false"] for request in deletes)

    @pytest.mark.asyncio
    async def test_bulk_stops_after_failure_and_reports_not_attempted(self, readarr, httpx_mock):
        requests = _mock_readarr(
            httpx_mock,
            books=[_book(11, "book-11"), _book(12, "book-12"), _book(13, "book-13")],
            delete_failures={12},
        )
        _, tools = _tools(readarr)

        result = await tools["readarr_delete_books"](
            book_ids=[11, 12, 13],
            dry_run=False,
        )

        assert result["success"] is False
        assert [request.url.path for request in _requests(requests, "DELETE")] == [
            f"{API_ROOT}/book/11",
            f"{API_ROOT}/book/12",
        ]
        assert 13 in result["data"]["not_attempted"]

    @pytest.mark.asyncio
    async def test_bulk_rejects_more_than_one_hundred_ids_without_reads_or_writes(self, readarr, httpx_mock):
        requests = _mock_readarr(httpx_mock, books=[])
        _, tools = _tools(readarr)

        result = await tools["readarr_delete_books"](book_ids=list(range(1, 102)))

        assert result["success"] is False
        assert _requests(requests, "GET") == []
        assert _requests(requests, "DELETE") == []

    @pytest.mark.asyncio
    async def test_bulk_rejects_bool_id_without_reads_or_writes(self, readarr, httpx_mock):
        requests = _mock_readarr(httpx_mock, books=[])
        _, tools = _tools(readarr)

        result = await tools["readarr_delete_books"](book_ids=[True])

        assert result["success"] is False
        assert _requests(requests, "GET") == []
        assert _requests(requests, "DELETE") == []

    @pytest.mark.asyncio
    async def test_bulk_preflight_rejects_response_id_mismatch_before_deleting(self, readarr, httpx_mock):
        requests = _mock_readarr(
            httpx_mock,
            books=[_book(11, "book-11")],
            book_response_overrides={11: _book(99, "book-11")},
        )
        _, tools = _tools(readarr)

        result = await tools["readarr_delete_books"](book_ids=[11], dry_run=False)

        assert result["success"] is False
        assert _requests(requests, "DELETE") == []
        assert result["data"]["preflight_errors"]
