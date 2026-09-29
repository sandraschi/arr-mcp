"""Regression tests for native post-add Radarr and Sonarr searches."""

from __future__ import annotations

import json

import httpx
import pytest

from arr_mcp.services.radarr_service import RadarrClient
from arr_mcp.services.sonarr_service import SonarrClient
from arr_mcp.tools.radarr_tools import register_radarr_tools
from arr_mcp.tools.sonarr_tools import register_sonarr_tools
from tests.conftest import MockMCP

API_KEY = "test-api-key"


def _recording_callback(
    requests: list[httpx.Request],
    responses: dict[tuple[str, str], tuple[int, dict]],
):
    def callback(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        status, payload = responses[(request.method, request.url.path)]
        return httpx.Response(status, json=payload)

    return callback


@pytest.mark.asyncio
async def test_radarr_search_preflights_movie_then_submits_exact_movie_command(httpx_mock):
    requests: list[httpx.Request] = []
    command = {"id": 100, "name": "MoviesSearch", "status": "queued"}
    httpx_mock.add_callback(
        _recording_callback(
            requests,
            {
                ("GET", "/api/v3/movie/42"): (200, {"id": 42, "title": "Dune"}),
                ("POST", "/api/v3/command"): (200, command),
            },
        ),
        is_reusable=True,
    )
    client = RadarrClient("http://localhost:7878", API_KEY)
    mcp = MockMCP()
    register_radarr_tools(mcp, client)

    try:
        result = await mcp.tools["radarr_movies"](operation="search", movie_id=42)
    finally:
        await client.close()

    assert result["success"] is True
    assert result["data"] == command
    assert [(request.method, request.url.path) for request in requests] == [
        ("GET", "/api/v3/movie/42"),
        ("POST", "/api/v3/command"),
    ]
    assert json.loads(requests[1].content) == {"name": "MoviesSearch", "movieIds": [42]}


@pytest.mark.asyncio
@pytest.mark.parametrize("movie_id", [None, 0, -1, True, False, 42.0, "42"])
async def test_radarr_search_rejects_invalid_exact_movie_id_without_http(httpx_mock, movie_id):
    client = RadarrClient("http://localhost:7878", API_KEY)
    mcp = MockMCP()
    register_radarr_tools(mcp, client)

    try:
        result = await mcp.tools["radarr_movies"](operation="search", movie_id=movie_id)
    finally:
        await client.close()

    assert result["success"] is False
    assert "movie_id" in result["message"]
    assert httpx_mock.get_requests() == []


@pytest.mark.asyncio
async def test_radarr_search_does_not_submit_when_preflight_id_mismatches(httpx_mock):
    httpx_mock.add_response(method="GET", url="http://localhost:7878/api/v3/movie/42", json={"id": 99})
    client = RadarrClient("http://localhost:7878", API_KEY)
    mcp = MockMCP()
    register_radarr_tools(mcp, client)

    try:
        result = await mcp.tools["radarr_movies"](operation="search", movie_id=42)
    finally:
        await client.close()

    assert result["success"] is False
    assert len(httpx_mock.get_requests()) == 1


@pytest.mark.asyncio
async def test_sonarr_series_search_preflights_series_then_submits_series_command(httpx_mock):
    requests: list[httpx.Request] = []
    command = {"id": 101, "name": "SeriesSearch", "status": "queued"}
    httpx_mock.add_callback(
        _recording_callback(
            requests,
            {
                ("GET", "/api/v3/series/7"): (200, {"id": 7, "title": "Severance"}),
                ("POST", "/api/v3/command"): (200, command),
            },
        ),
        is_reusable=True,
    )
    client = SonarrClient("http://localhost:8989", API_KEY)
    mcp = MockMCP()
    register_sonarr_tools(mcp, client)

    try:
        result = await mcp.tools["sonarr_series"](operation="search", series_id=7)
    finally:
        await client.close()

    assert result["success"] is True
    assert result["data"] == command
    assert json.loads(requests[1].content) == {"name": "SeriesSearch", "seriesId": 7}


@pytest.mark.asyncio
async def test_sonarr_episode_search_preflights_episode_then_submits_episode_command(httpx_mock):
    requests: list[httpx.Request] = []
    command = {"id": 102, "name": "EpisodeSearch", "status": "queued"}
    httpx_mock.add_callback(
        _recording_callback(
            requests,
            {
                ("GET", "/api/v3/episode/21"): (200, {"id": 21, "title": "Good News About Hell"}),
                ("POST", "/api/v3/command"): (200, command),
            },
        ),
        is_reusable=True,
    )
    client = SonarrClient("http://localhost:8989", API_KEY)
    mcp = MockMCP()
    register_sonarr_tools(mcp, client)

    try:
        result = await mcp.tools["sonarr_episodes"](operation="search", episode_id=21)
    finally:
        await client.close()

    assert result["success"] is True
    assert result["data"] == command
    assert json.loads(requests[1].content) == {"name": "EpisodeSearch", "episodeIds": [21]}


@pytest.mark.asyncio
@pytest.mark.parametrize("season_number", [0, 2])
async def test_sonarr_season_search_preflights_series_then_submits_season_command(httpx_mock, season_number):
    requests: list[httpx.Request] = []
    command = {"id": 103, "name": "SeasonSearch", "status": "queued"}
    httpx_mock.add_callback(
        _recording_callback(
            requests,
            {
                (
                    "GET",
                    "/api/v3/series/7",
                ): (
                    200,
                    {
                        "id": 7,
                        "title": "Severance",
                        "seasons": [{"seasonNumber": 0}, {"seasonNumber": 2}],
                    },
                ),
                ("POST", "/api/v3/command"): (200, command),
            },
        ),
        is_reusable=True,
    )
    client = SonarrClient("http://localhost:8989", API_KEY)
    mcp = MockMCP()
    register_sonarr_tools(mcp, client)

    try:
        result = await mcp.tools["sonarr_episodes"](operation="search", series_id=7, season_number=season_number)
    finally:
        await client.close()

    assert result["success"] is True
    assert result["data"] == command
    assert json.loads(requests[1].content) == {
        "name": "SeasonSearch",
        "seriesId": 7,
        "seasonNumber": season_number,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kwargs",
    [
        {},
        {"episode_id": 0},
        {"series_id": 7},
        {"season_number": 1},
        {"series_id": 7, "season_number": -1},
        {"episode_id": 21, "series_id": 7, "season_number": 2},
    ],
)
async def test_sonarr_episode_or_season_search_rejects_invalid_selection_without_http(httpx_mock, kwargs):
    client = SonarrClient("http://localhost:8989", API_KEY)
    mcp = MockMCP()
    register_sonarr_tools(mcp, client)

    try:
        result = await mcp.tools["sonarr_episodes"](operation="search", **kwargs)
    finally:
        await client.close()

    assert result["success"] is False
    assert httpx_mock.get_requests() == []


@pytest.mark.asyncio
async def test_sonarr_season_search_rejects_unknown_season_without_command(httpx_mock):
    httpx_mock.add_response(
        method="GET",
        url="http://localhost:8989/api/v3/series/7",
        json={"id": 7, "title": "Severance", "seasons": [{"seasonNumber": 1}]},
    )
    client = SonarrClient("http://localhost:8989", API_KEY)
    mcp = MockMCP()
    register_sonarr_tools(mcp, client)

    try:
        result = await mcp.tools["sonarr_episodes"](operation="search", series_id=7, season_number=2)
    finally:
        await client.close()

    assert result["success"] is False
    assert "does not exist" in result["message"]
    assert len(httpx_mock.get_requests()) == 1
