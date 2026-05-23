# arr-mcp — Product Requirements Document

**Version**: 1.2.0  
**Date**: 2026-05-22  
**Status**: Production-ready  

## Problem Statement

The *arr automation stack is powerful but fragmented. Users manage 6-8 separate web UIs (Radarr, Sonarr, Lidarr, Prowlarr, Readarr, Overseerr, Bazarr) with no unified control plane. Each has its own API, its own port, its own auth. Adding a new movie requires: (1) checking if it's already in Jellyfin, (2) opening Radarr, (3) searching, (4) adding. Cross-service queries (e.g., "what's downloading right now across all arrs?") require visiting 6 separate UIs.

## Solution

`arr-mcp` is a FastMCP 3.3 MCP server that wraps the entire *arr ecosystem behind a single, unified MCP interface. It provides:

1. **22 portmanteau MCP tools** — one tool per service + cross-arr orchestration
2. **Jellyfin availability bridge** — checks Jellyfin before queuing media
3. **Auto-discovery** — probes default ports for running services
4. **Conditional registration** — tools only exist for configured services
5. **25 total tools** covering 109+ operations

## Target Users

1. **MCP clients** (Claude Desktop, Cursor, Windsurf) — LLM agents use tools for media management
2. **Web dashboard users** — 15-page React PWA with health monitoring
3. **Developers** — Tauri 2.0 native desktop app

## Feature Matrix

### Phase 1 — Core Service Integration (DONE v1.0.0)

| Feature | Status |
|---------|--------|
| Radarr (Movies) — list, lookup, add, delete, import | Done |
| Sonarr (TV) — series CRUD, episode management | Done |
| Lidarr (Music) — artist CRUD, album management | Done |
| Prowlarr (Indexers) — indexer CRUD, unified search, app sync | Done |
| Readarr (Books) — author CRUD, book management | Done |
| Overseerr (Requests) — request CRUD, approve/decline, search | Done |
| Bazarr (Subtitles) — wanted, search, download, providers | Done |
| BaseArrClient — shared ~60% API surface | Done |
| Auto-discovery with port probing | Done |
| Conditional tool registration | Done |
| Jellyfin availability bridge | Done |

### Phase 2 — Cross-Orchestration (DONE v1.0.0)

| Feature | Status |
|---------|--------|
| `arr_orchestrate` — check Jellyfin → auto-route to correct arr | Done |
| `arr_calendar` — unified calendar across all arrs | Done |
| `arr_stats` — consolidated stack statistics | Done |
| `arr_health` — stack-wide health probing | Done |
| `arr_help` — tool discovery and quickstart | Done |
| `arr_agentic` — LLM-powered cross-arr workflows | Done |

### Phase 3 — Webapp (DONE v1.1.0)

| Feature | Status |
|---------|--------|
| 15-page React dashboard (Vite + Tailwind) | Done |
| SSE log streaming (`/api/logs/stream`) | Done |
| MCP Inspector with interactive tool runner | Done |
| PWA with installable manifest + service worker | Done |
| Desktop notifications | Done |
| Playwright e2e smoke tests | Done |

### Phase 4 — FastMCP 3.3+ & Prefab Cards (DONE v1.2.0)

| Feature | Status |
|---------|--------|
| FastMCP 3.3 env-var compliance (stateless_http, log_level) | Done |
| `arr_health_card` — Prefab-UI health card | Done |
| `arr_calendar_card` — Prefab-UI calendar card | Done |
| `arr_stats_card` — Prefab-UI stats card | Done |
| Resources: `arr://quickstart`, `arr://help`, `arr://capabilities` | Done |
| `sampling_handler_behavior="fallback"` | Done |
| Context injection via try/except import | Done |
| Calendar week calculation fix | Done |

### Phase 5 — Tauri Native (DONE v1.1.0)

| Feature | Status |
|---------|--------|
| Tauri 2.0 native app wrapper | Done |
| PyInstaller sidecar for Python backend | Done |
| Build pipeline: webapp → PyInstaller → Tauri → .exe | Done |

## Non-Goals

- **No standalone UI** — the webapp is optional; core value is MCP tools
- **No media playback** — this is an orchestrator, not a player
- **No download client management** — covered by Prowlarr + individual arrs
- **No Readarr revival** — Readarr is deprecated upstream, but existing instances still work

## Success Metrics

- [x] 143 tests passing
- [x] Ruff lint clean
- [x] Mypy typecheck clean (pre-existing exceptions excluded)
- [x] Playwright e2e: 15 pages smoke test pass
- [x] All 7 *arr services supported
- [x] Cross-arr orchestration with Jellyfin bridge
- [x] Prefab-UI cards in supporting clients
- [x] FastMCP 3.3+ compliant

## Fleet Standards Compliance

| Standard | Status |
|----------|--------|
| Portmanteau tool pattern | ✓ |
| FastMCP 3.2+ (`FastMCP`, `@mcp.tool`, `@mcp.resource`, `@mcp.prompt`) | ✓ |
| Pydantic v2 (`model_dump`, no `.dict()`) | ✓ |
| `uv` dependency management | ✓ |
| Ruff formatting (line-length=120, double quotes) | ✓ |
| justfile with fleet recipes | ✓ |
| GitHub Actions CI | ✓ |
| Prefab-UI cards | ✓ |
| .env.example | ✓ |
| AGENTS.md | ✓ |
| Ports 10938/10939 (fleet range) | ✓ |
