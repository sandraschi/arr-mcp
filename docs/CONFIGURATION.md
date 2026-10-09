# Configuration — arr-mcp

All configuration is via environment variables (`.env` at repo root) loaded by
`ArrConfig.load_config()` (`src/arr_mcp/config.py`). Copy `.env.example` to `.env` first.

## *arr services (each: URL + API key + enabled flag)

| Prefix | Default URL | Notes |
|---|---|---|
| `RADARR_` | http://localhost:7878 | Movies (`/api/v3`) |
| `SONARR_` | http://localhost:8989 | TV (`/api/v3`) |
| `LIDARR_` | http://localhost:8686 | Music (`/api/v1`) |
| `PROWLARR_` | http://localhost:9696 | Indexers (`/api/v1`) |
| `READARR_` | http://localhost:8787 | Books (`/api/v1`, upstream deprecated) |
| `OVERSEERR_` | http://localhost:5055 | Requests |
| `BAZARR_` | http://localhost:6767 | Subtitles (`/api`) |

Each service needs `<PREFIX>_URL`, `<PREFIX>_API_KEY` (Settings → General in the
*arr UI), and `<PREFIX>_ENABLED=true`. Unconfigured services skip tool
registration entirely. Auto-discovery: if an API key is set and the default port
is open locally, the client is created even with `ENABLED` unset.

## Media servers (orchestration availability checks)

`JELLYFIN_URL` + `JELLYFIN_API_KEY`, `PLEX_URL` + `PLEX_TOKEN`,
`EMBY_URL` + `EMBY_API_KEY`. Placeholder values (`your-*-here`, shipped in
`.env.example`) count as **unconfigured**. A configured-but-unreachable server is
skipped with a `<name>_error` pipeline step instead of aborting the request.

## Transport

`ARR_MCP_TRANSPORT` = `stdio` (default, Claude Desktop) | `http` | `sse`.
`ARR_MCP_HOST` (default 127.0.0.1), `ARR_MCP_PORT` (default 10938),
`ARR_MCP_PATH` (default `/mcp`). CLI flags `--http/--sse/--stdio --port N`
override env. Tauri sets `ARR_TAURI=1` which forces HTTP. Docker: run with
`ARR_MCP_TRANSPORT=http` (see `docker-compose.yml` `arr-mcp` service).

## Misc

`ARR_SAMPLING_BASE_URL` (default http://127.0.0.1:11434/v1),
`ARR_SAMPLING_MODEL` (default llama3.2), `ARR_SAMPLING_API_KEY` (optional),
`ARR_LOG_LEVEL` (default INFO), `ARR_TIMEOUT` (default 30s),
`FASTMCP_STATELESS_HTTP=1`, `FASTMCP_LOG_LEVEL`.
