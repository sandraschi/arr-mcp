"""Tests for cross-arr orchestration helpers and MCP tools."""

import pytest

from arr_mcp.config import ArrConfig
from arr_mcp.constants import ArrServiceName
from arr_mcp.tools.cross_arr_tools import (
    _stack_disk,
    _stack_history,
    _stack_queue,
    _stack_status,
    _stack_summary,
    register_cross_arr_tools,
)
from tests.conftest import MockArrClient, MockMCP


@pytest.fixture
def clients():
    return {
        "radarr": MockArrClient(version="5.1.0", movies=[{"id": 1, "title": "Dune"}]),
        "sonarr": None,
        "lidarr": None,
        "prowlarr": None,
        "readarr": None,
        "overseerr": None,
        "bazarr": None,
    }


class TestStackHelpers:
    @pytest.mark.asyncio
    async def test_stack_status_with_string_keys(self, clients):
        result = await _stack_status(clients)
        assert result["success"] is True
        assert result["data"]["radarr"]["reachable"] is True
        assert result["data"]["radarr"]["version"] == "5.1.0"
        assert result["data"]["sonarr"]["reachable"] is False

    @pytest.mark.asyncio
    async def test_stack_status_with_enum_keys(self):
        enum_clients = {
            ArrServiceName.RADARR: MockArrClient(),
            ArrServiceName.SONARR: None,
        }
        result = await _stack_status(enum_clients)
        assert "radarr" in result["data"]
        assert result["data"]["radarr"]["reachable"] is True

    @pytest.mark.asyncio
    async def test_stack_summary(self, clients):
        result = await _stack_summary(clients)
        assert result["success"] is True
        assert result["data"]["radarr"]["movies"] == 1
        assert result["data"]["sonarr"]["enabled"] is False

    @pytest.mark.asyncio
    async def test_stack_disk(self, clients):
        result = await _stack_disk(clients)
        assert result["success"] is True
        assert "radarr" in result["data"]

    @pytest.mark.asyncio
    async def test_stack_queue(self, clients):
        clients["radarr"].queue_records = [{"title": "Dune"}]
        result = await _stack_queue(clients)
        assert result["success"] is True
        assert result["data"]["radarr"]["totalRecords"] == 1

    @pytest.mark.asyncio
    async def test_stack_history(self, clients):
        clients["radarr"].history_records = [{"eventType": "downloadFolderImported"}]
        result = await _stack_history(clients)
        assert result["success"] is True
        assert len(result["data"]["radarr"]["records"]) == 1


class TestCrossArrTools:
    @pytest.fixture
    def mcp_tools(self, clients):
        mcp = MockMCP()
        config = ArrConfig()
        register_cross_arr_tools(mcp, clients, config)
        return mcp.tools

    @pytest.mark.asyncio
    async def test_arr_orchestrate_status(self, mcp_tools):
        result = await mcp_tools["arr_orchestrate"](operation="status")
        assert result["success"] is True
        assert "radarr" in result["data"]

    @pytest.mark.asyncio
    async def test_arr_orchestrate_queue(self, mcp_tools):
        result = await mcp_tools["arr_orchestrate"](operation="queue")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_arr_orchestrate_check_jellyfin_not_configured(self, mcp_tools):
        result = await mcp_tools["arr_orchestrate"](operation="check_jellyfin", media_title="Dune")
        assert result["success"] is True
        assert result["data"]["in_library"] is False

    @pytest.mark.asyncio
    async def test_arr_orchestrate_request_requires_title(self, mcp_tools):
        result = await mcp_tools["arr_orchestrate"](operation="request")
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_arr_orchestrate_request_adds_movie(self, clients, mcp_tools):
        clients["radarr"].lookup_movie_results = [{"tmdbId": 438631, "title": "Dune"}]
        result = await mcp_tools["arr_orchestrate"](
            operation="request",
            media_title="Dune",
            media_type="movie",
        )
        assert result["success"] is True
        assert "add_to_arr" in result["pipeline"]

    @pytest.mark.asyncio
    async def test_arr_calendar_upcoming(self, mcp_tools):
        result = await mcp_tools["arr_calendar"](operation="upcoming")
        assert result["success"] is True
        assert "radarr" in result["data"]

    @pytest.mark.asyncio
    async def test_arr_stats_summary(self, mcp_tools):
        result = await mcp_tools["arr_stats"](operation="summary")
        assert result["success"] is True
        assert "radarr" in result["data"]

    @pytest.mark.asyncio
    async def test_arr_stats_disk(self, mcp_tools):
        result = await mcp_tools["arr_stats"](operation="disk")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_arr_stats_queues(self, mcp_tools):
        result = await mcp_tools["arr_stats"](operation="queues")
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_arr_stats_history(self, mcp_tools):
        result = await mcp_tools["arr_stats"](operation="history")
        assert result["success"] is True
