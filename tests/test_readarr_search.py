"""Focused regression tests for the registered Readarr book search operation."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Annotated, Any, get_args, get_origin, get_type_hints

import httpx
import pytest
import pytest_asyncio
from pydantic import StrictInt

from arr_mcp.services.readarr_service import ReadarrClient
from arr_mcp.tools.readarr_tools import register_readarr_tools

READARR_URL = "http://localhost:8787/readarr"
API_ROOT = "/readarr/api/v1"
API_KEY = "test-api-key"


class RecordingMCP:
    """Small MCP stand-in that retains registered functions for direct calls."""

    def __init__(self) -> None:
        self.tools: dict[str, Callable[..., Any]] = {}

    def tool(self, **kwargs: Any):
        def decorator(fn: Callable[..., Any]):
            self.tools[fn.__name__] = fn
            return fn

        return decorator


@pytest_asyncio.fixture
async def readarr():
    client = ReadarrClient(READARR_URL, API_KEY)
    yield client
    await client.close()


def _book(book_id: int = 42) -> dict[str, Any]:
    return {"id": book_id, "title": "A Book", "authorId": 7}


def _mock_readarr_search(
    httpx_mock,
    *,
    book: dict[str, Any] | None = None,
    book_status: int = 200,
    command: dict[str, Any] | None = None,
    command_status: int = 200,
    lookup_results: list[dict[str, Any]] | None = None,
) -> list[httpx.Request]:
    requests: list[httpx.Request] = []

    def callback(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.method == "GET" and request.url.path == f"{API_ROOT}/book/42":
            if book_status != 200:
                return httpx.Response(book_status, json={"message": "book not found"})
            return httpx.Response(200, json=book if book is not None else _book())

        if request.method == "GET" and request.url.path == f"{API_ROOT}/book/lookup":
            return httpx.Response(200, json=lookup_results or [])

        if request.method == "POST" and request.url.path == f"{API_ROOT}/command":
            if command_status != 200:
                return httpx.Response(command_status, json={"message": "command rejected"})
            return httpx.Response(200, json=command or {"id": 123, "status": "queued"})

        raise AssertionError(f"unexpected mocked Readarr request: {request.method} {request.url}")

    httpx_mock.add_callback(callback, is_reusable=True, is_optional=True)
    return requests


def _tools(client: ReadarrClient) -> dict[str, Callable[..., Any]]:
    mcp = RecordingMCP()
    register_readarr_tools(mcp, client)
    return mcp.tools


def _requests(requests: list[httpx.Request], method: str, path: str | None = None) -> list[httpx.Request]:
    return [
        request
        for request in requests
        if request.method == method and (path is None or request.url.path == path)
    ]


class TestReadarrBookSearchRegistration:
    def test_search_is_registered_and_uses_strict_book_id_annotation(self):
        tools = _tools(object())  # type: ignore[arg-type]

        assert "readarr_books" in tools
        annotation = get_type_hints(tools["readarr_books"], include_extras=True)["book_id"]

        assert get_origin(annotation) is Annotated
        assert get_args(annotation)[0] == StrictInt | None


class TestReadarrBookSearch:
    @pytest.mark.asyncio
    async def test_search_preflights_exact_book_then_posts_one_book_search_command(
        self, readarr, httpx_mock
    ):
        command = {"id": 123, "status": "queued", "name": "BookSearch"}
        requests = _mock_readarr_search(httpx_mock, book=_book(), command=command)
        tools = _tools(readarr)

        result = await tools["readarr_books"](operation="search", book_id=42)

        assert result["success"] is True
        assert "42" in result["message"]
        assert "search" in result["message"].lower()
        assert result["data"] == command
        assert [(request.method, request.url.path) for request in requests] == [
            ("GET", f"{API_ROOT}/book/42"),
            ("POST", f"{API_ROOT}/command"),
        ]
        command_requests = _requests(requests, "POST", f"{API_ROOT}/command")
        assert len(command_requests) == 1
        assert json.loads(command_requests[0].content) == {"name": "BookSearch", "bookIds": [42]}

    @pytest.mark.asyncio
    @pytest.mark.parametrize("book_id", [None, 0, -1, True, False, 42.0, "42"])
    async def test_search_rejects_missing_non_positive_bool_or_non_int_id_without_http(
        self, readarr, httpx_mock, book_id
    ):
        requests = _mock_readarr_search(httpx_mock)
        tools = _tools(readarr)

        result = await tools["readarr_books"](operation="search", book_id=book_id)

        assert result["success"] is False
        assert "book_id" in result["message"]
        assert requests == []

    @pytest.mark.asyncio
    async def test_search_does_not_post_when_exact_book_is_missing(self, readarr, httpx_mock):
        requests = _mock_readarr_search(httpx_mock, book_status=404)
        tools = _tools(readarr)

        result = await tools["readarr_books"](operation="search", book_id=42)

        assert result["success"] is False
        assert _requests(requests, "GET", f"{API_ROOT}/book/42")
        assert _requests(requests, "POST", f"{API_ROOT}/command") == []

    @pytest.mark.asyncio
    async def test_search_does_not_post_when_preflight_returns_a_different_book_id(
        self, readarr, httpx_mock
    ):
        requests = _mock_readarr_search(httpx_mock, book=_book(99))
        tools = _tools(readarr)

        result = await tools["readarr_books"](operation="search", book_id=42)

        assert result["success"] is False
        assert "42" in result["message"]
        assert _requests(requests, "POST", f"{API_ROOT}/command") == []

    @pytest.mark.asyncio
    async def test_search_returns_failure_when_book_search_command_fails(self, readarr, httpx_mock):
        requests = _mock_readarr_search(httpx_mock, command_status=500)
        tools = _tools(readarr)

        result = await tools["readarr_books"](operation="search", book_id=42)

        assert result["success"] is False
        assert len(_requests(requests, "POST", f"{API_ROOT}/command")) == 1

    @pytest.mark.asyncio
    async def test_lookup_remains_read_only(self, readarr, httpx_mock):
        lookup_results = [{"foreignBookId": "book-42", "title": "A Book"}]
        requests = _mock_readarr_search(httpx_mock, lookup_results=lookup_results)
        tools = _tools(readarr)

        result = await tools["readarr_books"](operation="lookup", term="A Book")

        assert result == {
            "success": True,
            "message": "Found 1 results for 'A Book'",
            "data": lookup_results,
        }
        assert len(_requests(requests, "GET", f"{API_ROOT}/book/lookup")) == 1
        assert _requests(requests, "GET", f"{API_ROOT}/book/42") == []
        assert _requests(requests, "POST", f"{API_ROOT}/command") == []
