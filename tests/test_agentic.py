"""Tests for ``arr_agentic`` — LLM-sampled cross-arr workflows."""

import pytest

from arr_mcp.tools.agentic import register_agentic_tools
from tests.conftest import MockArrClient, MockMCP


@pytest.fixture
def agentic_tool():
    mcp = MockMCP()
    clients = {
        "radarr": MockArrClient(movies=[{"id": 1, "title": "Dune"}]),
        "sonarr": None,
        "lidarr": None,
        "readarr": None,
        "prowlarr": None,
        "overseerr": None,
        "bazarr": None,
    }
    register_agentic_tools(mcp, clients)
    return mcp.tools["arr_agentic"], clients


class TestArrAgentic:
    @pytest.mark.asyncio
    async def test_workflow_without_ctx(self, agentic_tool):
        tool, _ = agentic_tool
        result = await tool(operation="workflow", prompt="add The Matrix to Radarr")
        assert result["success"] is True
        assert result["data"]["sampling_used"] is False
        assert "radarr" in result["data"]["available_services"]

    @pytest.mark.asyncio
    async def test_natural_query_without_ctx(self, agentic_tool):
        tool, _ = agentic_tool
        result = await tool(operation="natural_query", prompt="what's my most wanted movie?")
        assert result["success"] is True
        assert result["data"]["sampling_used"] is False

    @pytest.mark.asyncio
    async def test_lists_available_services(self, agentic_tool):
        tool, clients = agentic_tool
        result = await tool(operation="workflow", prompt="status check")
        services = result["data"]["available_services"]
        assert "radarr" in services
        assert "sonarr" not in services
        assert "lidarr" not in services

    @pytest.mark.asyncio
    async def test_no_services_configured(self):
        mcp = MockMCP()
        clients: dict = {}
        register_agentic_tools(mcp, clients)
        tool = mcp.tools["arr_agentic"]

        result = await tool(operation="workflow", prompt="do something")
        assert result["success"] is True
        assert result["data"]["available_services"] == []

    @pytest.mark.asyncio
    async def test_returns_prompt_in_response(self, agentic_tool):
        tool, _ = agentic_tool
        result = await tool(operation="workflow", prompt="find me something good to watch")
        assert result["data"]["prompt"] == "find me something good to watch"
