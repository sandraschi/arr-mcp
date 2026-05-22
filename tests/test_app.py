"""Tests for FastMCP app factory."""

from arr_mcp import __version__
from arr_mcp.app import create_mcp
from arr_mcp.config import ArrConfig


class TestCreateMcp:
    def test_creates_fastmcp_instance(self):
        mcp = create_mcp(ArrConfig())
        assert mcp.name == "arr-mcp"

    def test_version_matches_package(self):
        assert __version__ == "1.0.0"
