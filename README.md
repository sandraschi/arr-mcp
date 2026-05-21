# arr-mcp

FastMCP 3.3 MCP server for the complete *arr automation stack — Radarr, Sonarr, Lidarr, Prowlarr, Readarr, Overseerr, and Bazarr — under a single MCP interface.

## Features

- **7 services, 1 MCP server** — Radarr (Movies), Sonarr (TV), Lidarr (Music), Prowlarr (Indexers), Readarr (Books), Overseerr (Requests), Bazarr (Subtitles)
- **Cross-arr orchestration** — request a title, auto-routes to correct arr with Jellyfin availability check
- **Prowlarr indexer backbone** — unified search across all indexers
- **Optional services** — each arr independently configurable via `.env`, disabled services don't register tools
- **Portmanteau tools** — one MCP tool per arr with `operation` parameter (20 tools total)
- **React dashboard** — 13-page webapp with health monitoring, LLM chat (Ollama/LM Studio), live logger
- **Local LLM chat** — built-in chat page with Ollama and LM Studio model selection

## Quick Start

```bash
# 1. Clone
git clone https://github.com/sandraschi/arr-mcp
cd arr-mcp

# 2. Create config
cp .env.example .env
# Edit .env — add your *arr URLs and API keys

# 3. Run
uv sync
uv run arr-mcp

# 4. Webapp (separate terminal)
cd webapp
npm install
npm run dev        # → http://localhost:10939
```

## Supported Services

| Service | Default Port | Config Prefix | Description |
|---------|-------------|---------------|-------------|
| Radarr | 7878 | `RADARR_` | Movies |
| Sonarr | 8989 | `SONARR_` | TV Series |
| Lidarr | 8686 | `LIDARR_` | Music |
| Prowlarr | 9696 | `PROWLARR_` | Indexer Backbone |
| Readarr | 8787 | `READARR_` | Books |
| Overseerr | 5055 | `OVERSEERR_` | Media Requests & Discovery |
| Bazarr | 6767 | `BAZARR_` | Subtitles |

## Setting Up the *Arr Stack

### Option 1: Docker Compose (recommended)

```bash
docker compose up -d
```

This starts all 8 services (7 *arrs + Jellyfin) with proper volume mounts. Services will be available at:

```
Radarr:    http://localhost:7878
Sonarr:    http://localhost:8989
Lidarr:    http://localhost:8686
Prowlarr:  http://localhost:9696
Readarr:   http://localhost:8787
Overseerr: http://localhost:5055
Bazarr:    http://localhost:6767
Jellyfin:  http://localhost:8096
```

### Option 2: Manual Installation

Install each service individually from their official sources:

- [Radarr](https://radarr.video) — Movies
- [Sonarr](https://sonarr.tv) — TV Series
- [Lidarr](https://lidarr.audio) — Music
- [Prowlarr](https://prowlarr.com) — Indexers
- [Readarr](https://readarr.com) — Books (use `:develop` tag, still in active development)
- [Overseerr](https://overseerr.dev) — Media Requests
- [Bazarr](https://www.bazarr.media) — Subtitles

### Getting API Keys

Every *arr service uses an API key for authentication. Get yours:

1. Open the service web UI (e.g. `http://localhost:7878`)
2. Go to **Settings → General**
3. Copy the **API Key**
4. Paste it into your `.env` file:
   ```
   RADARR_API_KEY=abc123...
   SONARR_API_KEY=def456...
   ```
5. Set `RADARR_ENABLED=true` etc. for each service

> Services with `ENABLED=false` or missing API key/URL will not register their MCP tools — no errors, no clutter.

### Connecting Prowlarr to Your *Arrs

Prowlarr is the indexer backbone. For full automation:

1. Open Prowlarr (`http://localhost:9696`)
2. Add indexers (NZBGeek, etc.)
3. Go to **Settings → Apps** and add Sonarr, Radarr, Lidarr, Readarr
4. Click **Sync App Indexers** — Prowlarr pushes indexers to all connected apps

## MCP Tools (20 total)

| Tool | Operations |
|------|-----------|
| `radarr_movies` | list, lookup, get, add, delete, update, import |
| `sonarr_series` | list, lookup, get, add, delete, update |
| `sonarr_episodes` | list, get, search, set_monitored |
| `lidarr_artists` | list, lookup, get, add, delete, update |
| `lidarr_albums` | list, get, lookup, set_monitored |
| `prowlarr_indexers` | list, get, add, update, delete, test, test_all, schema |
| `prowlarr_search` | unified search across all indexers |
| `prowlarr_applications` | list, get, sync, sync_all, test |
| `prowlarr_history` | list, since, by_indexer |
| `readarr_authors` | list, lookup, get, add, delete, update |
| `readarr_books` | list, get, lookup, set_monitored |
| `overseerr_requests` | list, get, create, approve, decline, delete, count, pending |
| `overseerr_search` | search TMDB for media |
| `overseerr_users` | list, get, requests |
| `bazarr_subtitles` | wanted, search, download, history, providers, languages |
| `arr_orchestrate` | request, status, check_jellyfin, queue |
| `arr_calendar` | upcoming, today, week, range |
| `arr_stats` | summary, disk, queues, history |
| `arr_health` | all, radarr, sonarr, lidarr, prowlarr, readarr, overseerr, bazarr |

## Webapp Pages (13)

- **Dashboard** — live health cards for all 7 services
- **Radarr / Sonarr / Lidarr / Prowlarr / Readarr / Overseerr / Bazarr** — per-service pages with tool references
- **Orchestrate** — cross-arr pipeline visualization
- **Chat** — AI chat with Ollama/LM Studio model selection
- **Logger** — live scrolling log viewer with filtering/download
- **Help** — full setup guide, Docker compose, per-service installation, API key retrieval, tool reference
- **Settings** — backend health, LLM provider config, port reference

## Cross-Arr Orchestration

```
"I want to watch Dune"
       ↓
  Jellyfin check → already in library? → DONE
       ↓ not found
  Type detection → movie → Radarr
       ↓
  Queue check → not already queued?
       ↓
  Add to Radarr → downloading...
```

## Project Structure

```
arr-mcp/
├── src/arr_mcp/          # Python backend
│   ├── services/         # 7 arr clients + 1 Jellyfin bridge
│   ├── tools/            # 20 portmanteau MCP tools
│   ├── utils/            # Jellyfin bridge
│   ├── app.py            # FastMCP singleton
│   ├── server.py         # Entry point, conditional registration
│   ├── config.py         # Pydantic v2 config
│   └── transport.py      # STDIO/HTTP/SSE runner
├── webapp/               # React 19 + Vite + Tailwind
│   └── src/pages/        # 13 page components
├── tests/                # pytest + pytest-httpx (40 tests)
├── docker-compose.yml    # Full *arr stack
├── justfile              # Fleet-standard recipes
└── pyproject.toml        # hatchling + uv + ruff
```

## Development

```bash
just install    # uv sync + pre-commit
just start      # run MCP server
just webapp     # start React dev server
just lint       # ruff + biome
just test       # pytest with coverage
just ci         # lint + test + webapp lint
```

## Ports

- Backend: **10938** (FastMCP HTTP `/mcp`)
- Frontend: **10939** (Vite React dashboard)

## License

MIT
