# Changelog

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
