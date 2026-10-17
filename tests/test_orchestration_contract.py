"""Regression tests: orchestration must call REAL client signatures.

The camelCase/snake_case mismatch (tmdbId= passed to add_movie(tmdb_id, ...))
slipped through because permissive mocks accept anything. These tests use the
real client classes with only the HTTP layer stubbed, so signature drift fails
loudly here instead of silently in production.
"""

from __future__ import annotations

import pytest

from arr_mcp.constants import MediaType
from arr_mcp.orchestration import add_to_arr, detect_media_type, request_media
from arr_mcp.services.lidarr_service import LidarrClient
from arr_mcp.services.radarr_service import RadarrClient
from arr_mcp.services.readarr_service import ReadarrClient
from arr_mcp.services.sonarr_service import SonarrClient


def _stub_http(client, get_result=None, post_result=None):
    captured: dict = {}

    async def fake_get(path, **params):
        return get_result if get_result is not None else []

    async def fake_post(path, json=None, **params):
        captured["path"] = path
        captured["json"] = json
        return post_result if post_result is not None else {"id": 1}

    client._get = fake_get  # noqa: SLF001 - stubbing HTTP layer only
    client._post = fake_post  # noqa: SLF001 - stubbing HTTP layer only
    return captured


@pytest.mark.asyncio
async def test_add_movie_uses_real_signature():
    client = RadarrClient("http://localhost:7878", "k")
    captured = _stub_http(client, get_result=[{"tmdbId": 438631, "title": "Dune"}])
    result = await add_to_arr(client, "Dune", MediaType.MOVIE, 1, "/movies")
    assert result == {"id": 1}
    assert captured["path"] == "/api/v3/movie"
    assert captured["json"]["tmdbId"] == 438631
    assert captured["json"]["qualityProfileId"] == 1
    assert captured["json"]["rootFolderPath"] == "/movies"


@pytest.mark.asyncio
async def test_add_series_uses_real_signature():
    client = SonarrClient("http://localhost:8989", "k")
    captured = _stub_http(client, get_result=[{"tvdbId": 121361, "title": "Severance"}])
    result = await add_to_arr(client, "Severance", MediaType.SERIES, 1, "/tv")
    assert result == {"id": 1}
    assert captured["json"]["tvdbId"] == 121361


@pytest.mark.asyncio
async def test_add_artist_uses_real_signature():
    client = LidarrClient("http://localhost:8686", "k")
    captured = _stub_http(client, get_result=[{"foreignArtistId": "mbid-1", "artistName": "NIN"}])
    result = await add_to_arr(client, "NIN", MediaType.ALBUM, 1, "/music")
    assert result == {"id": 1}
    assert captured["json"]["foreignArtistId"] == "mbid-1"


@pytest.mark.asyncio
async def test_add_author_uses_real_signature():
    client = ReadarrClient("http://localhost:8787", "k")
    captured = _stub_http(client, get_result=[{"foreignAuthorId": "auth-1", "authorName": "Sanderson"}])
    result = await add_to_arr(client, "Sanderson", MediaType.BOOK, 1, "/books")
    assert result == {"id": 1}
    assert captured["json"]["foreignAuthorId"] == "auth-1"


@pytest.mark.asyncio
async def test_add_reports_missing_foreign_id():
    client = RadarrClient("http://localhost:7878", "k")
    _stub_http(client, get_result=[{"title": "No ID here"}])
    result = await add_to_arr(client, "No ID here", MediaType.MOVIE, 1, "/movies")
    assert "error" in result
    assert "tmdbId" in result["error"]


@pytest.mark.asyncio
async def test_add_requires_root_folder():
    client = RadarrClient("http://localhost:7878", "k")

    async def fake_get(path, **params):
        if "rootfolder" in path or "rootFolder" in path:
            return []
        return [{"tmdbId": 438631, "title": "Dune"}]

    async def fake_post(path, json=None, **params):
        raise AssertionError("add must not be attempted without a root folder")

    client._get = fake_get  # noqa: SLF001
    client._post = fake_post  # noqa: SLF001
    result = await add_to_arr(client, "Dune", MediaType.MOVIE, 1, None)
    assert "error" in result
    assert "root folder" in result["error"]


@pytest.mark.asyncio
async def test_add_failure_is_structured():
    client = RadarrClient("http://localhost:7878", "k")

    async def fake_post(path, json=None, **params):
        raise RuntimeError("boom")

    _stub_http(client, get_result=[{"tmdbId": 438631, "title": "Dune"}])
    client._post = fake_post  # noqa: SLF001
    result = await add_to_arr(client, "Dune", MediaType.MOVIE, 1, "/movies")
    assert result["error"].startswith("add_movie failed:")


@pytest.mark.asyncio
async def test_request_media_end_to_end_with_real_client():
    client = RadarrClient("http://localhost:7878", "k")
    captured = _stub_http(
        client,
        get_result=[{"tmdbId": 438631, "title": "Dune"}],
    )

    async def fake_wanted():
        return {"records": []}

    async def fake_profiles():
        return [{"id": 1}]

    async def fake_folders():
        return [{"path": "/movies"}]

    client.get_wanted_missing = fake_wanted  # noqa: SLF001
    client.get_quality_profiles = fake_profiles  # noqa: SLF001
    client.get_root_folders = fake_folders  # noqa: SLF001

    result = await request_media({"radarr": client}, {}, "Dune", media_type="movie")
    assert result["success"] is True
    assert result["data"]["action"] == "added_to_radarr"
    assert captured["json"]["tmdbId"] == 438631


@pytest.mark.asyncio
async def test_detect_media_type_with_real_client():
    client = RadarrClient("http://localhost:7878", "k")
    _stub_http(client, get_result=[{"tmdbId": 1, "title": "Dune"}])
    assert await detect_media_type("Dune", {"radarr": client}) == MediaType.MOVIE
    assert await detect_media_type("zzznomatch", {"radarr": None}) is None
