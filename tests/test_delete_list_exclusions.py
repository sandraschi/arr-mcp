"""Regression coverage for Radarr and Sonarr delete-list exclusions."""

from __future__ import annotations

from urllib.parse import parse_qs

import httpx
import pytest

from arr_mcp.services.radarr_service import RadarrClient
from arr_mcp.services.sonarr_service import SonarrClient
from arr_mcp.tools.radarr_tools import register_radarr_tools
from arr_mcp.tools.sonarr_tools import register_sonarr_tools
from tests.conftest import MockMCP

API_KEY = "test-api-key"

DELETE_CASES = (
    pytest.param(
        RadarrClient,
        register_radarr_tools,
        "radarr_movies",
        "movie_id",
        "http://localhost:7878",
        "/api/v3/movie/42",
        "addImportExclusion",
        id="radarr",
    ),
    pytest.param(
        SonarrClient,
        register_sonarr_tools,
        "sonarr_series",
        "series_id",
        "http://localhost:8989",
        "/api/v3/series/42",
        "addImportListExclusion",
        id="sonarr",
    ),
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("client_type", "register", "tool_name", "id_parameter", "base_url", "path", "exclusion_query"),
    DELETE_CASES,
)
@pytest.mark.parametrize("status_code", [pytest.param(200, id="empty-200"), pytest.param(204, id="empty-204")])
@pytest.mark.parametrize("delete_files", [pytest.param(False, id="keep-files"), pytest.param(True, id="delete-files")])
@pytest.mark.parametrize(
    "exclusion",
    [
        pytest.param(None, id="default-exclusion-false"),
        pytest.param(False, id="explicit-exclusion-false"),
        pytest.param(True, id="exclusion-true"),
    ],
)
async def test_registered_delete_forwards_independent_native_flags_and_accepts_empty_success(
    httpx_mock,
    client_type,
    register,
    tool_name: str,
    id_parameter: str,
    base_url: str,
    path: str,
    exclusion_query: str,
    status_code: int,
    delete_files: bool,
    exclusion: bool | None,
):
    def callback(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code)

    httpx_mock.add_callback(callback)
    client = client_type(base_url, API_KEY)
    mcp = MockMCP()
    register(mcp, client)

    kwargs = {
        "operation": "delete",
        id_parameter: 42,
        "delete_files": delete_files,
    }
    if exclusion is not None:
        kwargs["add_import_list_exclusion"] = exclusion

    try:
        result = await mcp.tools[tool_name](**kwargs)
    finally:
        await client.close()

    assert result["success"] is True
    assert result["data"] == {}
    assert len(httpx_mock.get_requests()) == 1
    request = httpx_mock.get_requests()[0]
    assert request.method == "DELETE"
    assert request.url.path == path
    assert parse_qs(request.url.query.decode()) == {
        "deleteFiles": [str(delete_files).lower()],
        exclusion_query: [str(exclusion if exclusion is not None else False).lower()],
    }
