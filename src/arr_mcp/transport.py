"""Unified transport runner — STDIO / HTTP / SSE.

In HTTP mode, builds a FastAPI app with CORS, the REST API router,
and mounts the MCP ASGI app. In STDIO mode, runs bare.
"""

from __future__ import annotations

import logging
import os
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP

from arr_mcp import __version__

logger = logging.getLogger(__name__)


def run_server(
    mcp: FastMCP,
    server_name: str = "arr-mcp",
    api_router=None,
) -> None:
    transport, cli_port = parse_argv_flags()
    transport = os.getenv("ARR_MCP_TRANSPORT") or transport

    if transport == "stdio":
        logger.info("Starting %s in STDIO mode", server_name)
        mcp.run(transport="stdio")
    elif transport in ("http", "sse"):
        host = os.getenv("ARR_MCP_HOST", "127.0.0.1")
        port = int(os.getenv("ARR_MCP_PORT", str(cli_port or 10938)))
        path = os.getenv("ARR_MCP_PATH", "/mcp")
        logger.info("Starting %s in %s mode on %s:%d%s", server_name, transport.upper(), host, port, path)
        _run_http(mcp, server_name, host, port, path, transport, api_router)
    else:
        logger.error("Unknown transport %r — falling back to stdio", transport)
        mcp.run(transport="stdio")


def _run_http(
    mcp: FastMCP,
    server_name: str,
    host: str,
    port: int,
    path: str,
    transport: str,
    api_router=None,
) -> None:
    import uvicorn

    app = FastAPI(title=server_name, version=__version__)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if api_router:
        app.include_router(api_router)

        @app.get("/health")
        async def health_alias():
            from fastapi.responses import RedirectResponse

            return RedirectResponse("/api/health", status_code=307)

    mcp_app = mcp.http_app(path=path, transport=transport)
    app.mount("/", mcp_app)

    uvicorn.run(app, host=host, port=port, log_level="warning")


def parse_argv_flags() -> tuple[str, int | None]:
    """Parse transport and port flags from sys.argv."""
    transport = "stdio"
    port: int | None = None
    args = sys.argv[1:]
    index = 0
    while index < len(args):
        arg = args[index]
        if arg == "--http":
            transport = "http"
        elif arg == "--sse":
            transport = "sse"
        elif arg == "--stdio":
            transport = "stdio"
        elif arg == "--port" and index + 1 < len(args):
            port = int(args[index + 1])
            index += 1
        index += 1
    return transport, port


def resolve_transport_from_argv() -> str:
    """Return transport mode from CLI flags (legacy helper)."""
    return parse_argv_flags()[0]
