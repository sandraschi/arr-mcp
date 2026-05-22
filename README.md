# arr-mcp

FastMCP 3.3 MCP server for the complete *arr automation stack — Radarr, Sonarr, Lidarr, Prowlarr, Readarr, Overseerr, and Bazarr — under a single MCP interface.

## Features

- **7 services, 1 MCP server** — Radarr (Movies), Sonarr (TV), Lidarr (Music), Prowlarr (Indexers), Readarr (Books), Overseerr (Requests), Bazarr (Subtitles)
- **Cross-arr orchestration** — request a title, auto-routes to correct arr with Jellyfin availability check
- **Prowlarr indexer backbone** — unified search across all indexers
- **Auto-discovery** — probes default ports for running *arr services; no `.env` needed for standard setups
- **Optional services** — each arr independently configurable via `.env`, disabled services don't register tools
- **Portmanteau tools** — one MCP tool per arr with `operation` parameter (19 tools total)
- **React dashboard** — 15-page webapp with health monitoring, LLM chat, MCP Inspector, live SSE log streaming
- **Local LLM chat** — built-in chat page with Ollama and LM Studio model selection
- **PWA** — installable as desktop/mobile app with offline service worker
- **MCP Inspector** — interactive tool runner: select a tool, set params, execute via `/mcp`, see raw JSON-RPC response
- **Real-time logs** — SSE stream endpoint `/api/logs/stream` for live log viewing
- **Browser notifications** — desktop alerts for download completions / request approvals
- **Tauri 2.0 native** — single `.exe` installer bundling Python backend via PyInstaller
- **CI/CD** — GitHub Actions (ruff + pytest + biome + tsc), Playwright e2e smoke tests

## Quick Start

```bash
# 1. Clone
git clone https://github.com/sandraschi/arr-mcp
cd arr-mcp

# 2. Create config (optional — auto-discovery probes default ports)
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

## Webapp Pages (15)

| Page | Route | What it does |
|------|-------|-------------|
| **Dashboard** | `/` | Live health cards for all 7 services, polls every 15s |
| **Radarr / Sonarr / Lidarr / Prowlarr / Readarr / Overseerr / Bazarr** | `/{service}` | Live per-service data: counts, wanted, queue, disk space |
| **Orchestrate** | `/orchestrate` | Cross-arr pipeline viz, stack overview with total wanted |
| **Chat** | `/chat` | AI chat with Ollama/LM Studio model selection |
| **Inspector** | `/inspector` | Interactive MCP tool runner — select, param, execute |
| **Logger** | `/logger` | Real-time SSE log streaming with filter/export |
| **Help** | `/help` | Setup guide, Docker Compose, per-service install, API keys |
| **Settings** | `/settings` | LLM provider config, backend health, port reference |

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
├── src/arr_mcp/             # Python backend (FastMCP 3.3)
│   ├── services/            # 7 arr clients + Jellyfin bridge
│   ├── tools/               # 19 portmanteau MCP tools
│   ├── utils/               # Jellyfin bridge
│   ├── api.py               # REST router with /api/{service}/summary
│   ├── app.py               # FastMCP singleton
│   ├── server.py            # Entry point, auto-discovery, log buffer
│   ├── config.py            # Pydantic v2 config + .env loading
│   └── transport.py         # STDIO/HTTP/SSE + FastAPI CORS wrapper
├── webapp/                  # React 19 + Vite + Tailwind
│   ├── src/pages/           # 15 page components
│   ├── src/utils/           # apiFetch<T>(), notifications, LLM client
│   └── e2e/                 # Playwright smoke tests (15 pages)
├── native/                  # Tauri 2.0 app wrapper
│   ├── Cargo.toml           # Rust deps (tauri 2, shell/fs/process)
│   ├── src/main.rs          # Entry point, sidecar launch, cleanup
│   ├── tauri.conf.json      # Window config, sidecar path
│   ├── capabilities/        # Tauri 2.0 permission model
│   ├── icons/               # App icons
│   └── build-sidecar.ps1    # PyInstaller → binaries/
├── tests/                   # pytest + pytest-httpx (101 tests)
├── docker-compose.yml       # Full *arr stack (8 services)
├── .github/workflows/ci.yml # GitHub Actions (ruff + pytest + biome + tsc)
├── justfile                 # Fleet-standard recipes
├── arr-mcp-backend.spec     # PyInstaller spec
└── run_server.py            # PyInstaller entry point
```

## Development

```bash
just install       # uv sync + pre-commit
just start         # run MCP server
just webapp        # start React dev server
just lint          # ruff check
just typecheck     # mypy
just test          # pytest with coverage (101 tests)
just e2e           # Playwright e2e (starts backend + webapp)
just ci            # lint + typecheck + test + webapp build
just tauri-build   # full native installer
just tauri-dev     # Tauri hot-reload
just tauri-sidecar # PyInstaller backend only → native/binaries/
```

### E2E Tests (Playwright)

```bash
cd webapp
npm install
npx playwright install chromium
npm run test:e2e          # headless
npm run test:e2e:ui       # interactive UI
npm run test:e2e:headed   # visible browser
```

Playwright auto-starts the backend (`:10938`) and Vite dev server (`:10939`). 15 smoke tests verify every page loads without crashing.

## Ports

- Backend: **10938** (FastMCP HTTP `/mcp` + REST `/api/*` + SSE `/api/logs/stream`)
- Frontend: **10939** (Vite React dashboard)

## License

MIT
