"""Focused tests for safe Readarr add-options discovery."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

import pytest
import pytest_asyncio

from arr_mcp.constants import TOOL_VERSION
from arr_mcp.services.readarr_service import ReadarrClient
from arr_mcp.tools.readarr_options import register_readarr_options

READARR_URL = "http://localhost:8787/readarr"


class RecordingMCP:
    def __init__(self) -> None:
        self.tools: dict[str, Callable[..., Any]] = {}
        self.options: dict[str, dict[str, Any]] = {}

    def tool(self, **kwargs: Any):
        def decorator(fn: Callable[..., Any]):
            self.tools[fn.__name__] = fn
            self.options[fn.__name__] = kwargs
            return fn

        return decorator


class OptionsClient:
    async def get_root_folders(self) -> list[dict[str, Any]]:
        return [
            {
                "id": 1,
                "name": "Books",
                "path": "/books",
                "freeSpace": 123,
                "defaultQualityProfileId": 2,
                "defaultMetadataProfileId": 3,
                "defaultTags": [7],
                "calibreUrl": "http://calibre.internal",
                "calibreUsername": "admin",
                "calibrePassword": "calibre-secret",
                "apiKey": "root-secret",
            }
        ]

    async def get_quality_profiles(self) -> list[dict[str, Any]]:
        return [{"id": 2, "name": "Ebook", "apiKey": "quality-secret"}]

    async def get_metadata_profiles(self) -> list[dict[str, Any]]:
        return [{"id": 3, "name": "Book Metadata", "password": "metadata-secret"}]

    async def get_tags(self) -> list[dict[str, Any]]:
        return [{"id": 7, "label": "keep", "token": "tag-secret"}]


@pytest_asyncio.fixture
async def readarr():
    client = ReadarrClient(READARR_URL, "test-api-key")
    yield client
    await client.close()


def test_disabled_readarr_client_does_not_register_options_tool():
    mcp = RecordingMCP()

    register_readarr_options(mcp, None)

    assert "readarr_add_options" not in mcp.tools


@pytest.mark.asyncio
async def test_add_options_returns_only_sanitized_ui_choices():
    mcp = RecordingMCP()
    register_readarr_options(mcp, OptionsClient())

    result = await mcp.tools["readarr_add_options"]()

    assert result["success"] is True
    assert result["data"] == {
        "root_folders": [
            {
                "id": 1,
                "name": "Books",
                "path": "/books",
                "freeSpace": 123,
                "defaultQualityProfileId": 2,
                "defaultMetadataProfileId": 3,
                "defaultTags": [7],
            }
        ],
        "quality_profiles": [{"id": 2, "name": "Ebook"}],
        "metadata_profiles": [{"id": 3, "name": "Book Metadata"}],
        "tags": [{"id": 7, "label": "keep"}],
        "monitor_modes": ["specific_book", "all", "future", "missing", "existing", "first", "latest", "none"],
        "monitor_new_books_modes": ["all", "none", "new"],
    }
    assert mcp.options["readarr_add_options"] == {
        "annotations": {"readOnlyHint": True, "destructiveHint": False},
        "version": TOOL_VERSION,
    }
    assert "secret" not in json.dumps(result).lower()


@pytest.mark.asyncio
async def test_add_options_failure_uses_generic_message_without_leaking_error_data():
    class FailingOptionsClient(OptionsClient):
        async def get_metadata_profiles(self) -> list[dict[str, Any]]:
            raise RuntimeError("metadata-api-key=do-not-leak")

    mcp = RecordingMCP()
    register_readarr_options(mcp, FailingOptionsClient())

    result = await mcp.tools["readarr_add_options"]()

    assert result == {
        "success": False,
        "message": "Could not retrieve Readarr add options",
        "data": {},
    }
    assert "do-not-leak" not in json.dumps(result)


@pytest.mark.asyncio
async def test_get_metadata_profiles_uses_readarr_base_path(readarr, httpx_mock):
    httpx_mock.add_response(
        url=f"{READARR_URL}/api/v1/metadataprofile",
        json=[{"id": 3, "name": "Book Metadata"}],
    )

    result = await readarr.get_metadata_profiles()

    assert result == [{"id": 3, "name": "Book Metadata"}]
    request = httpx_mock.get_requests()[0]
    assert request.url.path == "/readarr/api/v1/metadataprofile"
