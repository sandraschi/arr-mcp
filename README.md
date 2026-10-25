# arr-mcp

<p align="center">
  <a href="https://github.com/sandraschi/arr-mcp"><img src="https://img.shields.io/github/stars/sandraschi/arr-mcp?style=flat-square" alt="Stars"></a>
  <a href="https://github.com/sandraschi/arr-mcp/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square" alt="License"></a>
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://github.com/PrefectHQ/fastmcp"><img src="https://img.shields.io/badge/FastMCP-3.4-7c5cfc?style=flat-square" alt="FastMCP"></a>
  <a href=""><img src="https://img.shields.io/badge/stack-*arr-00ADD8?style=flat-square" alt="*arr Stack"></a>
  <a href=""><img src="https://img.shields.io/badge/tests-289-success?style=flat-square" alt="Tests"></a>
  <a href=""><img src="https://img.shields.io/badge/fleet-SOTA-6366f1?style=flat-square" alt="Fleet SOTA"></a>
</p>

FastMCP 3.4 MCP server for the complete *arr automation stack — Radarr, Sonarr, Lidarr, Prowlarr, Readarr, Overseerr, and Bazarr — under a single MCP interface.

New here? Start at [`docs/ONBOARDING.md`](docs/ONBOARDING.md) (10-minute setup, no account needed).

## Install (Claude Desktop)

Download `arr-mcp.mcpb` + `install.ps1` from the
[latest release](https://github.com/sandraschi/arr-mcp/releases/latest/download/install.ps1),
then run `install.ps1` — it installs the bundle into Claude Desktop.
Other MCP clients (Cursor, Windsurf, opencode):

```json
{
  "mcpServers": {
    "arr-mcp": { "command": "uvx", "args": ["arr-mcp"] }
  }
}
```

## Features

- **7 services, 1 MCP server** — Radarr (Movies), Sonarr (TV), Lidarr (Music), Prowlarr (Indexers), Readarr (Books), Overseerr (Requests), Bazarr (Subtitles)
- **31 MCP tools** — portmanteau tools + single-purpose tools + 3 Prefab card tools
- **Cross-arr orchestration** — request a title, auto-routes to correct arr with Jellyfin availability check
- **Prefab-UI cards** — `arr_health_card`, `arr_calendar_card`, `arr_stats_card` (`@mcp.tool(app=True)`) — rich interactive cards in Claude Desktop, Cursor
- **Prowlarr indexer backbone** — unified search across all indexers
- **Auto-discovery** — probes default ports for running *arr services; no config needed for standard setups
- **Settings → Services** — paste URL + API key per service in the webapp, Test, Save: live immediately, no `.env`, no restart (`.env` still works as fallback)
- **FastMCP 3.3 resources** — `arr://config`, `arr://quickstart`, `arr://help`, `arr://capabilities` for agent self-discovery
- **LLM sampling** — `arr_agentic` tool with Context injection for LLM-powered cross-arr workflows
- **React dashboard** — 15-page webapp with health monitoring, LLM chat, MCP Inspector, live SSE log streaming
- **Local LLM chat** — built-in chat page with Ollama and LM Studio model selection (backend-proxied: keys never leave the server)
- **PWA** — installable as desktop/mobile app with offline service worker
- **MCP Inspector** — interactive tool runner: select a tool, set params, execute via `/mcp`, see raw JSON-RPC response
- **Real-time logs** — SSE stream endpoint `/api/logs/stream` for live log viewing
- **Browser notifications** — desktop alerts for download completions / request approvals
- **Tauri 2.0 native** — single `.exe` installer bundling Python backend via PyInstaller
- **CI/CD** — GitHub Actions (ruff + pytest + biome + tsc), 289 tests, Playwright e2e smoke tests

## Quick Start

```bash
# 1. Clone
git clone https://github.com/sandraschi/arr-mcp
cd arr-mcp

# 2. Create config (optional — auto-discovery probes default ports,
#    or use Settings → Services in the webapp later; no file editing needed)
cp .env.example .env

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
| **Dashboard** | `/` | KPIs (items/wanted/reachable), per-service cards with Open/Setup actions, detected Docker containers, fleet siblings |
| **Radarr / Sonarr / Lidarr / Prowlarr / Readarr / Overseerr / Bazarr** | `/{service}` | Live per-service data: counts, wanted, queue, disk space — or a setup guide when unconfigured |
| **Orchestrate** | `/orchestrate` | Request form (runs the real pipeline) + stack overview with total wanted |
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

The same pipeline runs from the webapp: the Orchestrate page has a request
form backed by `POST /api/orchestrate/request`.

## Fleet crossconnect (plex-mcp / jellyfin-mcp)

Three servers, three jobs: **arr-mcp acquires**, **plex-mcp owns Plex**,
**jellyfin-mcp owns Jellyfin**. arr-mcp checks your Plex/Jellyfin/Emby
*servers* directly before downloading — it does not route through the sibling
MCP servers, and nothing is shared between them. `GET /api/fleet` probes both
siblings live; the Dashboard links to their dashboards when running. Full
contract: [`docs/FLEET_MEDIA_TOPOLOGY.md`](docs/FLEET_MEDIA_TOPOLOGY.md).

## Project Structure

```
arr-mcp/
├── src/arr_mcp/             # Python backend (FastMCP 3.4)
│   ├── services/            # 8 arr clients (BaseArrClient + 7 arrs)
│   ├── tools/               # 31 MCP tools (portmanteau + single-purpose + prefab cards)
│   ├── prefabs.py           # Prefab-UI card builders (health, calendar, stats, orchestrate)
│   ├── utils/               # Jellyfin bridge
│   ├── api.py               # REST router with /api/{service}/summary
│   ├── app.py               # FastMCP singleton, lifespan, resources, prompts
│   ├── server.py            # Entry point, auto-discovery, log buffer
│   ├── config.py            # Pydantic v2 config + .env loading
│   └── transport.py         # STDIO/HTTP/SSE + FastMCP 3.3 env vars
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
├── tests/                   # pytest + pytest-httpx (289 tests)
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
just test          # pytest with coverage (289 tests)
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

## Docker (remote hosting)

```bash
docker compose up -d arr-mcp              # backend on :10938 (HTTP transport)
docker compose --profile webapp up -d     # dashboard on :10939
```

The `arr-mcp` service builds `Dockerfile` (uv, locked deps) with
`ARR_MCP_TRANSPORT=http`; config comes from the repo-root `.env`.
Point MCP clients at `http://HOST:10938/mcp`. See `docs/TROUBLESHOOTING.md`
for container networking notes (use compose service names, not `localhost`).

## Bugs

Bug reports and feature requests go to [GitHub Issues](../../issues) using the
issue forms (a bug report needs version + reproducer, no exceptions).
GitHub is also where PRs happen; questions belong in
[Discussions](../../discussions). Never post secrets or API keys — redact and
rotate first; security-sensitive reports go through a
[private advisory](../../security/advisories/new).

## License

MIT
