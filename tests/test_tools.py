"""Tests for portmanteau MCP tools across all *arr services."""

import pytest

from arr_mcp.tools.bazarr_tools import register_bazarr_tools
from arr_mcp.tools.lidarr_tools import register_lidarr_tools
from arr_mcp.tools.overseerr_tools import register_overseerr_tools
from arr_mcp.tools.prowlarr_tools import register_prowlarr_tools
from arr_mcp.tools.radarr_tools import register_radarr_tools
from arr_mcp.tools.readarr_tools import register_readarr_tools
from arr_mcp.tools.sonarr_tools import register_sonarr_tools
from tests.conftest import MockArrClient, MockMCP
from tests.mock_clients import (
    MockBazarrClient,
    MockLidarrClient,
    MockOverseerrClient,
    MockProwlarrClient,
    MockReadarrClient,
    MockSonarrClient,
)


@pytest.fixture
def radarr_tool():
    mcp = MockMCP()
    client = MockArrClient(
        movies=[{"id": 1, "title": "Dune"}],
        lookup_movie_results=[{"title": "Dune", "tmdbId": 438631}],
        add_movie_result={"id": 2, "title": "Dune"},
    )
    register_radarr_tools(mcp, client)
    return mcp.tools["radarr_movies"], client


class TestRadarrTools:
    @pytest.mark.asyncio
    async def test_list_movies(self, radarr_tool):
        tool, _client = radarr_tool
        result = await tool(operation="list")
        assert result["success"] is True
        assert len(result["data"]) == 1

    @pytest.mark.asyncio
    async def test_lookup_requires_term(self, radarr_tool):
        tool, _client = radarr_tool
        result = await tool(operation="lookup")
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_lookup_movie(self, radarr_tool):
        tool, _client = radarr_tool
        result = await tool(operation="lookup", term="Dune")
        assert result["success"] is True
        assert result["data"][0]["tmdbId"] == 438631

    @pytest.mark.asyncio
    async def test_add_requires_fields(self, radarr_tool):
        tool, _client = radarr_tool
        result = await tool(operation="add", tmdb_id=438631)
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_skips_registration_when_client_none(self):
        mcp = MockMCP()
        register_radarr_tools(mcp, None)
        assert "radarr_movies" not in mcp.tools


class TestSonarrTools:
    @pytest.fixture
    def tools(self):
        mcp = MockMCP()
        register_sonarr_tools(mcp, MockSonarrClient())
        return mcp.tools

    @pytest.mark.asyncio
    async def test_list_series(self, tools):
        result = await tools["sonarr_series"](operation="list")
        assert result["success"] is True
        assert result["data"][0]["title"] == "Breaking Bad"

    @pytest.mark.asyncio
    async def test_list_episodes(self, tools):
        result = await tools["sonarr_episodes"](operation="list", series_id=1)
        assert result["success"] is True
        assert len(result["data"]) == 1

    @pytest.mark.asyncio
    async def test_skips_when_unconfigured(self):
        mcp = MockMCP()
        register_sonarr_tools(mcp, None)
        assert "sonarr_series" not in mcp.tools


class TestLidarrTools:
    @pytest.fixture
    def tools(self):
        mcp = MockMCP()
        register_lidarr_tools(mcp, MockLidarrClient())
        return mcp.tools

    @pytest.mark.asyncio
    async def test_list_artists(self, tools):
        result = await tools["lidarr_artists"](operation="list")
        assert result["success"] is True
        assert result["data"][0]["artistName"] == "Nine Inch Nails"

    @pytest.mark.asyncio
    async def test_list_albums(self, tools):
        result = await tools["lidarr_albums"](operation="list", artist_id=1)
        assert result["success"] is True
        assert result["data"][0]["title"] == "The Downward Spiral"


class TestProwlarrTools:
    @pytest.fixture
    def tools(self):
        mcp = MockMCP()
        register_prowlarr_tools(mcp, MockProwlarrClient())
        return mcp.tools

    @pytest.mark.asyncio
    async def test_list_indexers(self, tools):
        result = await tools["prowlarr_indexers"](operation="list")
        assert result["success"] is True
        assert result["data"][0]["name"] == "NZBGeek"

    @pytest.mark.asyncio
    async def test_search(self, tools):
        result = await tools["prowlarr_search"](query="Dune 1080p")
        assert result["success"] is True
        assert "Dune" in result["data"][0]["title"]

    @pytest.mark.asyncio
    async def test_list_applications(self, tools):
        result = await tools["prowlarr_applications"](operation="list")
        assert result["success"] is True
        assert result["data"][0]["name"] == "Radarr"


class TestReadarrTools:
    @pytest.fixture
    def tools(self):
        mcp = MockMCP()
        register_readarr_tools(mcp, MockReadarrClient())
        return mcp.tools

    @pytest.mark.asyncio
    async def test_list_authors(self, tools):
        result = await tools["readarr_authors"](operation="list")
        assert result["success"] is True
        assert result["data"][0]["authorName"] == "Brandon Sanderson"

    @pytest.mark.asyncio
    async def test_list_books(self, tools):
        result = await tools["readarr_books"](operation="list", author_id=1)
        assert result["success"] is True
        assert result["data"][0]["title"] == "Mistborn"


class TestOverseerrTools:
    @pytest.fixture
    def tools(self):
        mcp = MockMCP()
        register_overseerr_tools(mcp, MockOverseerrClient())
        return mcp.tools

    @pytest.mark.asyncio
    async def test_list_requests(self, tools):
        result = await tools["overseerr_requests"](operation="list")
        assert result["success"] is True
        assert len(result["data"]["results"]) == 1

    @pytest.mark.asyncio
    async def test_search(self, tools):
        result = await tools["overseerr_search"](query="Dune")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_list_users(self, tools):
        result = await tools["overseerr_users"](operation="list")
        assert result["success"] is True
        assert result["data"]["results"][0]["displayName"] == "Admin"


class TestBazarrTools:
    @pytest.fixture
    def tools(self):
        mcp = MockMCP()
        register_bazarr_tools(mcp, MockBazarrClient())
        return mcp.tools

    @pytest.mark.asyncio
    async def test_wanted(self, tools):
        result = await tools["bazarr_subtitles"](operation="wanted")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_providers(self, tools):
        result = await tools["bazarr_subtitles"](operation="providers")
        assert result["success"] is True
        assert result["data"][0]["name"] == "opensubtitles"

    @pytest.mark.asyncio
    async def test_languages(self, tools):
        result = await tools["bazarr_subtitles"](operation="languages")
        assert result["success"] is True
        assert result["data"][0]["code2"] == "en"
