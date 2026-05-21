"""Tests for Jellyfin bridge cross-arr orchestration and tool registration."""

import pytest

from arr_mcp.constants import MediaType
from arr_mcp.utils.jellyfin_bridge import JellyfinBridge


class TestJellyfinBridge:
    def test_not_configured_by_default(self):
        bridge = JellyfinBridge("", "")
        assert not bridge.is_configured

    def test_configured_with_url_and_key(self):
        bridge = JellyfinBridge("http://localhost:8096", "test-key")
        assert bridge.is_configured

    @pytest.mark.asyncio
    async def test_search_not_configured(self):
        bridge = JellyfinBridge("", "")
        results = await bridge.search("Dune")
        assert results == []

    @pytest.mark.asyncio
    async def test_check_availability_not_configured(self):
        bridge = JellyfinBridge("", "")
        result = await bridge.check_availability("Dune")
        assert result["in_library"] is False
        assert result["note"] == "Jellyfin not configured"

    @pytest.mark.asyncio
    async def test_search_returns_items(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:8096/Items?searchTerm=Dune&IncludeItemTypes=Movie%2CSeries&Recursive=true&Limit=10",
            json={"Items": [{"Id": "abc123", "Name": "Dune", "Type": "Movie", "ProductionYear": 2021}]},
        )
        bridge = JellyfinBridge("http://localhost:8096", "test-key")
        results = await bridge.search("Dune")
        assert len(results) == 1
        assert results[0]["Name"] == "Dune"
        await bridge.close()

    @pytest.mark.asyncio
    async def test_find_title_exists(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:8096/Items?searchTerm=Dune&IncludeItemTypes=Movie&Recursive=true&Limit=10",
            json={"Items": [{"Id": "abc123", "Name": "Dune", "Type": "Movie", "ProductionYear": 2021}]},
        )
        bridge = JellyfinBridge("http://localhost:8096", "test-key")
        item = await bridge.find_title("Dune", MediaType.MOVIE)
        assert item is not None
        assert item["Name"] == "Dune"
        await bridge.close()

    @pytest.mark.asyncio
    async def test_find_title_not_found(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:8096/Items?searchTerm=NonExistent&IncludeItemTypes=Movie%2CSeries&Recursive=true&Limit=10",
            json={"Items": []},
        )
        bridge = JellyfinBridge("http://localhost:8096", "test-key")
        item = await bridge.find_title("NonExistent")
        assert item is None
        await bridge.close()

    @pytest.mark.asyncio
    async def test_check_availability_found(self, httpx_mock):
        httpx_mock.add_response(
            url="http://localhost:8096/Items?searchTerm=Inception&IncludeItemTypes=Movie&Recursive=true&Limit=10",
            json={"Items": [{"Id": "xyz789", "Name": "Inception", "Type": "Movie", "ProductionYear": 2010}]},
        )
        bridge = JellyfinBridge("http://localhost:8096", "test-key")
        result = await bridge.check_availability("Inception", MediaType.MOVIE)
        assert result["in_library"] is True
        assert result["matched_title"] == "Inception"
        assert result["jellyfin_id"] == "xyz789"
        await bridge.close()
