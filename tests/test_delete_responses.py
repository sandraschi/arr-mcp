"""Regression tests for successful and failed DELETE response handling."""

from __future__ import annotations

import json
from typing import Any

import httpx
import pytest

from arr_mcp.services.overseerr_service import OverseerrClient
from arr_mcp.services.radarr_service import RadarrClient
from arr_mcp.services.readarr_service import ReadarrClient
from arr_mcp.services.sonarr_service import SonarrClient

API_KEY = "test-api-key"
RADARR_URL = "http://localhost:7878"
SONARR_URL = "http://localhost:8989"
READARR_URL = "http://localhost:8787"
OVERSEERR_URL = "http://localhost:5055"

DELETE_CASES = (
    pytest.param(
        "radarr_movie",
        f"{RADARR_URL}/api/v3/movie/11?deleteFiles=true&addImportExclusion=false",
        id="radarr-delete-movie-with-files",
    ),
    pytest.param(
        "sonarr_episode_file",
        f"{SONARR_URL}/api/v3/episodefile/22",
        id="sonarr-delete-episode-file",
    ),
    pytest.param(
        "readarr_book_file",
        f"{READARR_URL}/api/v1/bookfile/33",
        id="readarr-delete-book-file",
    ),
    pytest.param(
        "radarr_blocklist_bulk",
        f"{RADARR_URL}/api/v3/blocklist/bulk",
        id="radarr-delete-blocklist-bulk",
    ),
    pytest.param(
        "overseerr_request",
        f"{OVERSEERR_URL}/api/v1/request/44",
        id="overseerr-delete-request",
    ),
)


def _client_for(operation: str) -> Any:
    if operation in {"radarr_movie", "radarr_blocklist_bulk"}:
        return RadarrClient(RADARR_URL, API_KEY)
    if operation == "sonarr_episode_file":
        return SonarrClient(SONARR_URL, API_KEY)
    if operation == "readarr_book_file":
        return ReadarrClient(READARR_URL, API_KEY)
    return OverseerrClient(OVERSEERR_URL, API_KEY)


async def _invoke_delete(client: Any, operation: str) -> dict[str, Any]:
    if operation == "radarr_movie":
        return await client.delete_movie(11, delete_files=True)
    if operation == "sonarr_episode_file":
        return await client.delete_episode_file(22)
    if operation == "readarr_book_file":
        return await client.delete_book_file(33)
    if operation == "radarr_blocklist_bulk":
        return await client.delete_blocklist_bulk([7, 8])
    return await client.delete_request(44)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("status_code", "content"),
    [
        pytest.param(200, b"", id="200-empty"),
        pytest.param(204, b"", id="204-empty"),
        pytest.param(200, b" \t\n", id="200-whitespace"),
    ],
)
@pytest.mark.parametrize(("operation", "url"), DELETE_CASES)
async def test_delete_accepts_successful_empty_responses(
    httpx_mock, operation: str, url: str, status_code: int, content: bytes
) -> None:
    client = _client_for(operation)
    httpx_mock.add_response(url=url, method="DELETE", status_code=status_code, content=content)

    try:
        assert await _invoke_delete(client, operation) == {}
    finally:
        await client.close()

    request = httpx_mock.get_requests()[0]
    if operation == "radarr_blocklist_bulk":
        assert json.loads(request.content) == {"ids": [7, 8]}


@pytest.mark.asyncio
@pytest.mark.parametrize(("operation", "url"), DELETE_CASES)
async def test_delete_preserves_nonempty_json_response(httpx_mock, operation: str, url: str) -> None:
    client = _client_for(operation)
    response = {"deleted": True, "operation": operation}
    httpx_mock.add_response(url=url, method="DELETE", json=response)

    try:
        assert await _invoke_delete(client, operation) == response
    finally:
        await client.close()

    if operation == "radarr_blocklist_bulk":
        assert json.loads(httpx_mock.get_requests()[0].content) == {"ids": [7, 8]}


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code", [pytest.param(404, id="client-error"), pytest.param(503, id="server-error")])
@pytest.mark.parametrize(
    ("operation", "url"),
    [
        pytest.param(
            "radarr_movie",
            f"{RADARR_URL}/api/v3/movie/11?deleteFiles=true&addImportExclusion=false",
            id="arr-client",
        ),
        pytest.param("overseerr_request", f"{OVERSEERR_URL}/api/v1/request/44", id="overseerr-client"),
    ],
)
async def test_delete_raises_for_http_errors_before_empty_body_fallback(
    httpx_mock, operation: str, url: str, status_code: int
) -> None:
    client = _client_for(operation)
    httpx_mock.add_response(url=url, method="DELETE", status_code=status_code, content=b"")

    try:
        with pytest.raises(httpx.HTTPStatusError) as exc_info:
            await _invoke_delete(client, operation)
        assert exc_info.value.response.status_code == status_code
    finally:
        await client.close()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("operation", "url"),
    [
        pytest.param(
            "radarr_movie",
            f"{RADARR_URL}/api/v3/movie/11?deleteFiles=true&addImportExclusion=false",
            id="arr-client",
        ),
        pytest.param("overseerr_request", f"{OVERSEERR_URL}/api/v1/request/44", id="overseerr-client"),
    ],
)
async def test_delete_does_not_swallow_nonempty_invalid_json(httpx_mock, operation: str, url: str) -> None:
    client = _client_for(operation)
    httpx_mock.add_response(url=url, method="DELETE", status_code=200, content=b"not-json")

    try:
        with pytest.raises(json.JSONDecodeError):
            await _invoke_delete(client, operation)
    finally:
        await client.close()
