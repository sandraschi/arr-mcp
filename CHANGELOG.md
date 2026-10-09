
## [Unreleased] — 2026-10-09

### Fixed (assfix)
- Issue #2: `_delete` tolerates empty 200 bodies (Servarr DELETE returns `{}` instead of JSONDecodeError false-failure) + regression test.
- Issue #1: placeholder `.env.example` credentials count as unconfigured (all three media bridges); unreachable media servers yield `<name>_error` pipeline steps instead of aborting orchestration + regression test.
- CORS: frontend `:10939` origins added; origin regex unconditional (LAN/Tailscale); webapp uses same-origin + Tauri-gated absolute URLs; vite proxy target honors `VITE_API_TARGET`.
- MCPB manifest: `${PWD}` → `${__dirname}`; regenerated 25-tool list; `scripts/mcpb-pack.ps1` is now the fleet shim.
- CI: Node 22, push/PR triggers, `ruff format --check` step. Ruff: `S110`/`S112` no longer silenced (clean).
- `just serve` + `just certify` recipes; `uv.lock` committed; `reports/` gitignored.

### Added (assfix)
- REST: `GET /api/capabilities|skills|v1/diagnostics`, `GET /api/llm/discover|providers|models|onboarding`, `POST /api/llm/chat|chat` (backend LLM proxy, skill-first), `POST /api/shutdown`; MCP tool `arr_shutdown`.
- Chat is backend-proxied (no direct browser→provider fetch); ChatPage loads skill status + backend LLM detection (Zustand store).
- `docs/`: CONFIGURATION, DEVELOPMENT, TOOLS, TROUBLESHOOTING, ONBOARDING; `skills/arr-mcp/SKILL.md`; `llms.txt`, `llms-full.txt`, `glama.json`; session-injection files; `renovate.json`; `.gitattributes`; fleet pre-commit template + vendored scripts.
- Docker: `Dockerfile` (backend) + `webapp/Dockerfile` + compose `arr-mcp`/`webapp` services (issue #5); Dashboard hero; per-page `data-testid` coverage.

## [Unreleased] — 2026-06-14

### Added
- Tauri CORS: 	auri://localhost, http://tauri.localhost, https://tauri.localhost in CORS origins
- Tauri CORS: _TAURI env var toggle with llow_origin_regex for secure WebView access
- build.ps1: auto-copy NSIS installer to dist/ on build
- CUA-NSIS: config-driven smoke test (`scripts/cua-smoke.py`, `scripts/cua-nsis-config.json`)
- CUA-NSIS: `just build-native` + `just cua-nsis-test` recipes
- CUA-NSIS: 11-phase smoke (install, launch, WebView OCR, feature route, diagnostics, uninstall)
- CUA-NSIS: local certification — all 11 phases pass locally (2026-06-14)

### Changed
- CORS: llow_origins=["*"] → explicit origins list for Tauri webview compatibility
# Changelog

## 1.2.0 (2026-05-22)

- **Prefab-UI cards**: `arr_health_card`, `arr_calendar_card`, `arr_stats_card` — rich interactive cards in supporting MCP clients (Claude Desktop, Cursor)
- **FastMCP 3.3+ compliance**: set `FASTMCP_STATELESS_HTTP=1` and `FASTMCP_LOG_LEVEL` via env; removed deprecated constructor kwargs (`debug`, `log_level`, `stateless_http`)
- **Additional resources**: `arr://quickstart`, `arr://help`, `arr://capabilities` — agent-self-discovery resources
- **Additional prompt**: `stack_health_check` — prompt for probing the full *arr stack
- **`sampling_handler_behavior="fallback"`** — explicit sampling fallback on FastMCP instance
- **Context injection**: fixed `Context` import (try/except fleet pattern), `arr_agentic` uses proper `Context | None` type
- **Calendar fix**: replaced `__import__("datetime").timedelta` with proper `from datetime import timedelta` import
- **Tool count**: 25 tools (22 portmanteau + 3 Prefab card tools), 109+ operations
- Ruff clean, mypy clean, 143 tests passing

## 1.1.0 (2026-05-21)

- GitHub Actions CI: backend (ruff + pytest + cov) + webapp (biome + tsc + build)
- SSE log stream endpoint (`/api/logs/stream`) with real-time EventSource
- LoggerPage: tries SSE first, falls back to 2s polling
- MCP Inspector page: interactive tool runner with param editor + JSON-RPC response
- PWA: vite-plugin-pwa with installable manifest + workbox service worker
- Desktop notifications: browser Notification API via `utils/notifications.ts`
- Playwright e2e: config + 15 page smoke tests (each page loads without crash)
- Sidebar: added Inspector link; 15-page webapp nav
- `apiFetch<T>()` with AbortController timeout (5s default)
- API_BASE for Tauri production builds (`import.meta.env.DEV ? "" : "http://...`)
- Adopt godot-mcp patterns: build-sidecar.ps1, .spec file, icon generator, SSE UI
- 101 tests passing, ruff clean, TypeScript clean, Biome clean

## 1.0.0 (2026-05-21)

- REST API router with per-service live data endpoints (`/api/{service}/summary`)
- All per-arr pages fetch real data (counts, wanted, queue, disk)
- Dashboard polls backend `/health` every 15s with live reachability
- Logger polls `/api/logs` every 2s with real backend log buffer
- Orchestrate page shows live orchestrator summary
- Auto-discovery: probes default ports for running *arr services
- Shared ServicePage component for all arr pages (DRY pattern)
- Tauri 2.0 native app wrapper (main.rs, tauri.conf.json, build.ps1)
- Log buffer (deque maxlen=500) with BufferHandler for webapp
- Transport: FastAPI wrapper with CORS and REST API router

## 0.4.0 (2026-05-21)

- docker-compose.yml: full *arr stack (8 services) one-command launch
- REST /health endpoint (FastAPI + CORS) returns live service status
- Help page: expandable per-service install guide, API key locations,
  Docker Compose instructions, tool reference
- README: complete setup guide, Docker/manual install, API key retrieval,
  Prowlarr connection guide, project structure, 20-tool reference table

## 0.3.0 (2026-05-21)

- Chat page with Ollama + LM Studio model selection, streaming chat UI
- LLM config persistence via localStorage (provider, URL, model)
- Logger page with live log stream, filtering, download, pause/resume
- Help page with full MCP tool reference (19 tools), quick start guide
- Settings page with backend health check, LLM config, port reference
- Updated Sidebar with bottom nav for Chat/Logger/Help/Settings

## 0.2.0 (2026-05-21)

- Overseerr service client (5055) — media requests, discovery, approval
- overseerr_requests / overseerr_search / overseerr_users portmanteau tools
- React webapp (Vite + React 19 + Tailwind + Biome) on port 10939
- 9-page dashboard: Dashboard, Radarr, Sonarr, Lidarr, Prowlarr, Readarr,
  Overseerr, Bazarr, Orchestrate
- Dark theme with per-arr color accents, sidebar nav, health status cards

## 0.1.0 (2026-05-21)

- Initial scaffold: FastMCP 3.2.4+, hatchling, uv
- Radarr tools: movie list, lookup, add, delete, import
- Sonarr tools: series list, lookup, add, delete; episode management
- Lidarr tools: artist list, lookup, add, delete; album management
- Prowlarr tools: indexer CRUD, unified search, app sync, history
- Readarr tools: author list, lookup, add, delete; book management
- Bazarr tools: subtitle search, download, wanted list, providers
- Cross-arr orchestration with Jellyfin availability bridge
- Stack-wide health check and consolidated stats
