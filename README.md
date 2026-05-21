# arr-mcp

FastMCP 3.2.4+ MCP server for the complete *arr automation stack — Radarr, Sonarr, Lidarr, Prowlarr, Readarr, and Bazarr — under a single MCP interface.

## Features

- **Unified *arr control** — one MCP server, six backend services
- **Cross-arr orchestration** — request a title, auto-routes to correct arr with Jellyfin availability check
- **Prowlarr indexer backbone** — unified search across all indexers
- **Bazarr subtitle tools** — search, download, and feed jellyfin-mcp RAG pipeline
- **Optional services** — each arr independently configurable via `.env`
- **Portmanteau tools** — one tool per arr with `operation` parameter

## Quick Start

```bash
cp .env.example .env
# Edit .env with your *arr URLs and API keys
uv sync
uv run arr-mcp
```

## Supported Services

| Service | Default Port | Config Prefix |
|---------|-------------|---------------|
| Radarr (Movies) | 7878 | `RADARR_` |
| Sonarr (TV) | 8989 | `SONARR_` |
| Lidarr (Music) | 8686 | `LIDARR_` |
| Prowlarr (Indexers) | 9696 | `PROWLARR_` |
| Readarr (Books) | 8787 | `READARR_` |
| Overseerr (Requests) | 5055 | `OVERSEERR_` |
| Bazarr (Subtitles) | 6767 | `BAZARR_` |

## Cross-Arr Orchestration

```python
# "I want to watch Dune"
arr_orchestrate(operation="request", media_title="Dune")
# → checks Jellyfin → if not found → adds to Radarr

# "I want The Expanse"
arr_orchestrate(operation="request", media_title="The Expanse")
# → checks Jellyfin → if not found → adds to Sonarr
```

## License

MIT
