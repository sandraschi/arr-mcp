# arr-mcp — Claude Code Guide

## Overview
FastMCP >=3.4.4,<4 MCP server for the complete *arr automation stack
(Radarr, Sonarr, Lidarr, Prowlarr, Readarr, Overseerr, Bazarr) with cross-arr
orchestration and Jellyfin/Plex/Emby bridge.

## Entry Points
- `uv run arr-mcp` → `arr_mcp.server:main` (stdio for Claude Desktop)
- `python -m arr_mcp --http --port 10938` → HTTP (webapp, Tauri, MCPB hosts)
- Ports: backend `:10938` (`/api/*`, `/mcp`), frontend `:10939` (Vite)

## Standards
- FastMCP portmanteau tool pattern — tools use `operation` enum param
- Responses: structured dicts with `success`, `message`, domain-specific fields
- Every tool docstring carries `## Return Format` + `## Examples`
- Dual transport: stdio (Claude Desktop) + HTTP (`ARR_MCP_TRANSPORT=http`)
- Prefab card tools use `@mcp.tool(app=True)` and return `prefab_ui` components
- See [mcp-central-docs](https://github.com/sandraschi/mcp-central-docs) for fleet-wide coding standards

## Key Files
- `README.md` — full documentation
- `pyproject.toml` — build config and entry points
- `AGENTS.md` — agent context (architecture, ports, tool catalog)
- `src/arr_mcp/server.py` — entry point, auto-discovery, log buffer
- `src/arr_mcp/transport.py` — STDIO/HTTP/SSE + CORS
- `src/arr_mcp/api.py` — REST router (`/api/*`)
- `docs/TOOLS.md` — per-tool reference (update when tools change)
