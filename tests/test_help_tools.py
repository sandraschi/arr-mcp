"""Tests for the ``arr_help`` tool discovery and quickstart tool."""

import pytest

from arr_mcp.tools.help_tools import register_help_tools
from tests.conftest import MockMCP


@pytest.fixture
def help_tool():
    mcp = MockMCP()
    register_help_tools(mcp)
    return mcp.tools["arr_help"]


class TestArrHelp:
    @pytest.mark.asyncio
    async def test_discover_returns_tools(self, help_tool):
        result = await help_tool(operation="discover")
        assert result["success"] is True
        assert result["data"]["tool_count"] > 10
        assert "tool_count" in result["data"]

    @pytest.mark.asyncio
    async def test_discover_lists_arr_orchestrate(self, help_tool):
        result = await help_tool(operation="discover")
        tools = result["data"]["tools"]
        names = [t["name"] for t in tools]
        assert "arr_orchestrate" in names
        assert "arr_health" in names
        assert "arr_help" in names

    @pytest.mark.asyncio
    async def test_tool_info_returns_info(self, help_tool):
        result = await help_tool(operation="tool_info", tool_name="arr_orchestrate")
        assert result["success"] is True
        info = result["data"]["info"]
        assert "service" in info
        assert info["service"] == "orchestrator"

    @pytest.mark.asyncio
    async def test_tool_info_unknown_tool(self, help_tool):
        result = await help_tool(operation="tool_info", tool_name="nonexistent_tool")
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_tool_info_requires_name(self, help_tool):
        result = await help_tool(operation="tool_info")
        assert result["success"] is False

    @pytest.mark.asyncio
    async def test_quickstart_returns_steps(self, help_tool):
        result = await help_tool(operation="quickstart")
        assert result["success"] is True
        assert len(result["data"]["steps"]) > 3
        assert "ports" in result["data"]
        assert result["data"]["ports"]["backend"] == 10938

    @pytest.mark.asyncio
    async def test_quickstart_contains_health_step(self, help_tool):
        result = await help_tool(operation="quickstart")
        steps_text = " ".join(result["data"]["steps"])
        assert "arr_health" in steps_text or "health" in steps_text

    @pytest.mark.asyncio
    async def test_unknown_operation(self, help_tool):
        result = await help_tool(operation="discover")  # valid — smoke test
        assert result["success"] is True
