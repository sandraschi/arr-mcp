# arr-mcp Agent Context

arr-mcp is a unified FastMCP 3.3+ server for the *arr automation stack (Radarr, Sonarr, Lidarr, Prowlarr, Readarr, Overseerr, Bazarr) with cross-arr orchestration and Jellyfin bridge.

## Architecture

```
server.py → create_mcp() → register_*_tools(mcp, client) → run_server()
```

Each service is independently optional. Disabled services skip tool registration entirely. Config via `.env` — see `.env.example`.

## FastMCP 3.3+ Patterns

- **Context import**: `try: from fastmcp import Context` with `except ImportError: from fastmcp.server.context import Context` (legacy fallback)
- **Env vars only**: `FASTMCP_STATELESS_HTTP=1`, `FASTMCP_LOG_LEVEL` — constructor kwargs removed in 3.3
- **`sampling_handler_behavior="fallback"`** — set on FastMCP instance
- **Resources**: `arr://config`, `arr://quickstart`, `arr://help`, `arr://capabilities`
- **Prompts**: `orchestrate_media`, `stack_health_check`
- **Prefab-UI**: `from prefab_ui.components import Card, Badge, Metric, Row` (>=0.18.0)

## Key Tools

- `radarr_movies` — movie lifecycle (list/lookup/add/delete/update/import)
- `sonarr_series` + `sonarr_episodes` — TV lifecycle
- `lidarr_artists` + `lidarr_albums` — music lifecycle
- `readarr_authors` + `readarr_books` — book lifecycle
- `prowlarr_indexers` + `prowlarr_search` + `prowlarr_applications` + `prowlarr_history` — indexer backbone
- `overseerr_requests` + `overseerr_search` + `overseerr_users` — media request management
- `bazarr_subtitles` — subtitle management (feeds jellyfin-mcp RAG)
- `arr_health` — stack-wide health probe
- `arr_orchestrate` — **differentiator**: given a title, checks Jellyfin → auto-routes to correct arr
- `arr_calendar` — unified calendar across all arrs
- `arr_stats` — consolidated stack statistics
- `arr_health_card` — rich Prefab card of stack health (in supporting clients)
- `arr_calendar_card` — rich Prefab card of upcoming releases
- `arr_stats_card` — rich Prefab card of stack statistics
- `arr_help` — tool discovery and quickstart
- `arr_agentic` — LLM-sampled cross-arr workflows (uses `ctx: Context | None`)

## Tool Registration Pattern

Tools are registered **imperatively** via `register_*_tools(mcp, client)` functions. Each tool file contains a `register_` function that applies `@mcp.tool()` decorators. This allows conditional registration — if a service client is `None`, its tools are simply not registered.

## Testing

- **143 tests** in `tests/` — pytest + pytest-httpx for HTTP mocking
- All service clients mocked with `tests/mock_clients.py`
- Ruff lint + mypy typecheck pre-commit hooks
- `uv run pytest tests/ -q` — run full suite

## Ports

| Service | Port |
|---------|------|
| arr-mcp backend | 10938 |
| arr-mcp frontend | 10939 |

Install docs: follow mcp-central-docs/standards/AGENT_INSTALL_REFERENCE.md
