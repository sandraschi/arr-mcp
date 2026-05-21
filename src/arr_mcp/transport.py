"""Unified transport runner — STDIO / HTTP / SSE.

Shared pattern across the fleet (cf. jellyfin-mcp, plex-mcp).
"""

from __future__ import annotations

import logging
import os
import sys

from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def run_server(mcp: FastMCP, server_name: str = "arr-mcp") -> None:
    """Resolve transport from CLI args / env and start the server."""

    transport = os.getenv("ARR_MCP_TRANSPORT") or resolve_transport_from_argv()

    if transport == "stdio":
        logger.info("Starting %s in STDIO mode", server_name)
        mcp.run(transport="stdio")
    elif transport in ("http", "sse"):
        host = os.getenv("ARR_MCP_HOST", "127.0.0.1")
        port = int(os.getenv("ARR_MCP_PORT", "10938"))
        path = os.getenv("ARR_MCP_PATH", "/mcp")
        logger.info("Starting %s in %s mode on %s:%d%s", server_name, transport.upper(), host, port, path)
        mcp.run(transport=transport, host=host, port=port, path=path)
    else:
        logger.error("Unknown transport %r — falling back to stdio", transport)
        mcp.run(transport="stdio")


def resolve_transport_from_argv() -> str:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    flag_map: dict[str, str] = {}
    for _i, a in enumerate(sys.argv[1:]):
        if a == "--http":
            return "http"
        if a == "--sse":
            return "sse"
        if a == "--stdio":
            return "stdio"
    for a in args:
        if a in flag_map:
            return flag_map[a]
    return "stdio"
