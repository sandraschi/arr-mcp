"""HTTP-level regression tests for Readarr book mutations."""

from __future__ import annotations

import json
from urllib.parse import parse_qs

import pytest
import pytest_asyncio

from arr_mcp.services.readarr_service import ReadarrClient

READARR_URL = "http://localhost:8787/readarr"
API_KEY = "test-api-key"


@pytest_asyncio.fixture
async def readarr():
    client = ReadarrClient(READARR_URL, API_KEY)
    yield client
    await client.close()


class TestReadarrBookMutationService:
    @pytest.mark.asyncio
    async def test_add_book_posts_nested_author_and_disabled_search_by_default(self, readarr, httpx_mock):
        httpx_mock.add_response(
            url=f"{READARR_URL}/api/v1/book",
            method="POST",
            json={"id": 42, "foreignBookId": "book-123"},
        )

        author = {
            "id": 7,
            "foreignAuthorId": "author-7",
            "qualityProfileId": 2,
            "metadataProfileId": 3,
            "path": "/books/author-7",
            "monitored": True,
        }
        result = await readarr.add_book(
            foreign_book_id="book-123",
            author=author,
        )

        assert result == {"id": 42, "foreignBookId": "book-123"}
        request = httpx_mock.get_requests()[0]
        assert request.method == "POST"
        assert request.url.path == "/readarr/api/v1/book"
        assert request.headers["X-Api-Key"] == API_KEY
        assert json.loads(request.content) == {
            "foreignBookId": "book-123",
            "monitored": True,
            "author": author,
            "addOptions": {"searchForNewBook": False},
        }

    @pytest.mark.asyncio
    async def test_add_book_can_explicitly_enable_search_without_changing_path(self, readarr, httpx_mock):
        httpx_mock.add_response(
            url=f"{READARR_URL}/api/v1/book",
            method="POST",
            json={"id": 43},
        )

        await readarr.add_book(
            foreign_book_id="book-456",
            author={"id": 7, "foreignAuthorId": "author-7"},
            search_for_new_book=True,
        )

        request = httpx_mock.get_requests()[0]
        body = json.loads(request.content)
        assert body["foreignBookId"] == "book-456"
        assert body["addOptions"] == {"searchForNewBook": True}
        assert request.url.path == "/readarr/api/v1/book"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("status_code", [200, 204])
    async def test_delete_book_accepts_successful_empty_response_and_query_flags(
        self, readarr, httpx_mock, status_code
    ):
        httpx_mock.add_response(
            url=f"{READARR_URL}/api/v1/book/42?deleteFiles=false&addImportListExclusion=true",
            method="DELETE",
            status_code=status_code,
        )

        result = await readarr.delete_book(
            42,
            delete_files=False,
            add_import_list_exclusion=True,
        )

        assert result == {}
        request = httpx_mock.get_requests()[0]
        assert request.method == "DELETE"
        assert request.url.path == "/readarr/api/v1/book/42"
        assert parse_qs(request.url.query.decode()) == {
            "deleteFiles": ["false"],
            "addImportListExclusion": ["true"],
        }
