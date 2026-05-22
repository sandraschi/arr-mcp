"""Tests for stack health MCP tools."""

import pytest

from arr_mcp.tools.health_tools import register_health_tools
from tests.conftest import MockArrClient, MockMCP


@pytest.fixture
def health_tool():
    mcp = MockMCP()
    clients = {
        "radarr": MockArrClient(version="5.0.0"),
        "sonarr": None,
        "lidarr": MockArrClient(version="4.0.0"),
        "prowlarr": None,
        "readarr": None,
        "overseerr": None,
        "bazarr": None,
    }
    register_health_tools(mcp, clients)
    return mcp.tools["arr_health"], clients


class TestHealthTools:
    @pytest.mark.asyncio
    async def test_arr_health_all(self, health_tool):
        tool, _clients = health_tool
        result = await tool(service="all")
        assert result["success"] is True
        assert result["data"]["radarr"]["reachable"] is True
        assert result["data"]["radarr"]["version"] == "5.0.0"
        assert result["data"]["sonarr"]["reachable"] is False
        assert "2/7" in result["message"]

    @pytest.mark.asyncio
    async def test_arr_health_single_service(self, health_tool):
        tool, _clients = health_tool
        result = await tool(service="radarr")
        assert result["success"] is True
        assert len(result["data"]) == 1
        assert result["data"]["radarr"]["reachable"] is True

    @pytest.mark.asyncio
    async def test_arr_health_unconfigured_service(self, health_tool):
        tool, _clients = health_tool
        result = await tool(service="sonarr")
        assert result["success"] is False
        assert result["data"]["sonarr"]["reason"] == "not configured"
