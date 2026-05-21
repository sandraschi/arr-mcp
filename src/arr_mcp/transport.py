"""Unified transport runner — STDIO / HTTP / SSE.

Shared pattern across the fleet (cf. jellyfin-mcp, plex-mcp).

In HTTP mode, builds a FastAPI app with CORS that wraps the MCP ASGI app
and exposes a REST ``/health`` endpoint for the webapp dashboard.
"""

from __future__ import annotations

import logging
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastmcp import FastMCP

logger = logging.getLogger(__name__)


def run_server(
    mcp: FastMCP,
    server_name: str = "arr-mcp",
    health_data_builder=None,
) -> None:
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
        _run_http_with_health(mcp, server_name, host, port, path, transport, health_data_builder)
    else:
        logger.error("Unknown transport %r — falling back to stdio", transport)
        mcp.run(transport="stdio")


def _run_http_with_health(
    mcp: FastMCP,
    server_name: str,
    host: str,
    port: int,
    path: str,
    transport: str,
    health_data_builder=None,
) -> None:
    """Run HTTP/SSE transport with a REST /health endpoint."""

    import uvicorn

    app = FastAPI(title=server_name, version="0.2.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health_endpoint():
        if health_data_builder:
            try:
                data = await health_data_builder()
                return JSONResponse(content={"success": True, "message": "ok", "data": data})
            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "message": str(e), "data": {}},
                )
        return JSONResponse(content={"success": True, "message": "arr-mcp is running", "data": {}})

    # Mount the MCP ASGI app at the configured path
    mcp_app = mcp.http_app(path=path, transport=transport)
    app.mount("/", mcp_app)

    uvicorn.run(app, host=host, port=port, log_level="warning")


def resolve_transport_from_argv() -> str:
    for a in sys.argv[1:]:
        if a == "--http":
            return "http"
        if a == "--sse":
            return "sse"
        if a == "--stdio":
            return "stdio"
    return "stdio"
