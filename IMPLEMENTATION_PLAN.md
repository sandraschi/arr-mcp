# `arr-mcp` — Implementation Plan

**Author**: Sandra Schipal
**Date**: 2026-05-21
**Status**: AWAITING APPROVAL

---

## Research Summary

### API Landscape

| Service | Version | Port | API Version | Primary Resources | Status |
|---------|---------|------|-------------|-------------------|--------|
| **Radarr** | v6.1.1 | 7878 | v3 | Movie, MovieFile | Active |
| **Sonarr** | v4.0.17 | 8989 | v3 (v3=v4 API) | Series, Episode | Active |
| **Lidarr** | v3.1.0 | 8686 | v1 | Artist, Album, Track | Active |
| **Prowlarr** | v2.3.5 | 9696 | v1 | Indexer, Application, Search | Active |
| **Bazarr** | v1.5.6 | 6767 | Custom REST | Movies, Episodes, Subtitles | Active |
| **Readarr** | retired | 8787 | v1 | Author, Book | ARCHIVED Jun 2025 |

**Critical finding**: Sonarr v3 and v4 share the **exact same API (v3)** — the OpenAPI spec explicitly states this. Radarr/Sonarr use `/api/v3/`, Lidarr/Prowlarr use `/api/v1/` (Lidarr forked before the v3 upgrade). All Servarr-based apps share **~60% of their API surface** (System, Health, Queue, History, Command, Calendar, Backup, DiskSpace, Log, Tag, CustomFormat, Notification, etc.).

**Readarr is dead**: The project was archived June 2025 (Goodreads metadata source died, OpenLibrary migration stalled). Community mirrors exist. The tool module will exist but be flagged as `DEPRECATED` with a clear warning.

**Bazarr is a separate codebase** (Python, not .NET). No shared Servarr API. Its REST API is simpler — about 15 endpoints. Token-based auth (not API key header like Servarr).

### Fleet Pattern References

Studied: `jellyfin-mcp`, `plex-mcp`, `calibre-mcp`. All follow identical patterns:
- `hatchling` + `uv-dynamic-versioning`, UV exclusively
- `fastmcp>=3.2.0`, Pydantic v2, `prefab-ui>=0.18.0`
- Ruff (line-length=120, double quotes) + Biome (frontend)
- Portmanteau tool pattern: `operation` Literal, `@mcp.tool()` at import time
- `BaseService` abstractions with async httpx
- justfile: `install`, `start`, `webapp`, `lint`, `fix`, `fmt`, `test`, `ci`, `clean`
- GitHub Actions: ci, release, industrial-launch, version-bump
- Tauri 2.0 native wrapper (jellyfin-mcp); DXT/MCPB (plex-mcp, calibre-mcp)

### Fleet Port Allocation

| Service | Port |
|---------|------|
| arr-mcp backend | 10982 |
| arr-mcp frontend | 10983 |

---

## Architecture

```
arr-mcp/
├── justfile
├── pyproject.toml
├── .env.example
├── .pre-commit-config.yaml
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── release.yml
│       ├── industrial-launch.yml
│       └── version-bump.yml
├── src/
│   └── arr_mcp/
│       ├── __init__.py
│       ├── __main__.py
│       ├── app.py              # FastMCP instance, lifespan, prompts
│       ├── server.py           # Entry point, tool imports, Starlette app
│       ├── config.py           # ArrConfig (Pydantic v2, .env loading)
│       ├── transport.py        # STDIO/HTTP/SSE runner
│       ├── prefabs.py          # prefab-ui status cards
│       ├── models/
│       │   ├── __init__.py     # Re-exports
│       │   ├── common.py       # Shared *arr models (QueueItem, HealthCheck, etc.)
│       │   ├── radarr.py       # Movie, MovieFile
│       │   ├── sonarr.py       # Series, Episode
│       │   ├── lidarr.py       # Artist, Album, Track
│       │   ├── prowlarr.py     # Indexer, Application
│       │   ├── bazarr.py       # Subtitle, Movie, Episode
│       │   └── readarr.py      # Author, Book (DEPRECATED)
│       ├── services/
│       │   ├── __init__.py     # Re-exports
│       │   ├── base.py         # BaseArrClient — shared ~60% API surface
│       │   ├── radarr.py       # RadarrClient(BaseArrClient)
│       │   ├── sonarr.py       # SonarrClient(BaseArrClient)
│       │   ├── lidarr.py       # LidarrClient(BaseArrClient)
│       │   ├── prowlarr.py     # ProwlarrClient(BaseArrClient)
│       │   ├── bazarr.py       # BazarrClient (separate, no Servarr base)
│       │   ├── readarr.py      # ReadarrClient(BaseArrClient) — DEPRECATED
│       │   ├── jellyfin_bridge.py  # HTTP check availability in Jellyfin
│       │   └── orchestrator.py # Cross-arr orchestration logic
│       ├── tools/
│       │   ├── __init__.py     # Conditional registration logic
│       │   ├── portmanteau/
│       │   │   ├── __init__.py # Imports only configured arr tools
│       │   │   ├── radarr.py   # radarr_media (portmanteau)
│       │   │   ├── sonarr.py   # sonarr_media (portmanteau)
│       │   │   ├── lidarr.py   # lidarr_media (portmanteau)
│       │   │   ├── prowlarr.py # prowlarr_indexer (portmanteau)
│       │   │   ├── bazarr.py   # bazarr_subtitle (portmanteau)
│       │   │   ├── readarr.py  # readarr_media (DEPRECATED)
│       │   │   ├── health.py   # arr_stack_health (all-arr status)
│       │   │   ├── orchestrate.py  # arr_orchestrate (cross-arr + Jellyfin)
│       │   │   ├── help.py     # arr_help
│       │   │   └── reporting.py    # arr_reporting
│       │   └── agentic.py      # Dynamic LLM tool registration
│       └── utils/
│           └── __init__.py     # get_logger(), sanitize helpers
├── tests/
│   ├── unit/
│   │   ├── test_base_client.py
│   │   ├── test_radarr.py
│   │   ├── test_sonarr.py
│   │   ├── test_lidarr.py
│   │   ├── test_prowlarr.py
│   │   ├── test_bazarr.py
│   │   ├── test_orchestrator.py
│   │   └── test_config.py
│   └── conftest.py
├── webapp/
│   ├── start.ps1
│   ├── backend/
│   │   └── app/
│   │       ├── main.py         # FastAPI, CORS, /health, /mcp mount
│   │       ├── config.py
│   │       └── api/
│   │           ├── radarr.py, sonarr.py, lidarr.py
│   │           ├── prowlarr.py, bazarr.py
│   │           ├── health.py, orchestrator.py
│   │           └── help.py
│   └── frontend/
│       ├── package.json        # next 15.2, react, tailwind, biome, playwright
│       ├── biome.json
│       ├── next.config.js      # API rewrites to backend port
│       ├── playwright.config.ts
│       └── app/
│           ├── layout.tsx, page.tsx
│           ├── radarr/, sonarr/, lidarr/
│           ├── prowlarr/, bazarr/
│           ├── health/, orchestrate/
│           ├── settings/, help/
│           └── components/
└── native/
    ├── Cargo.toml
    ├── build.rs
    ├── tauri.conf.json
    ├── src/main.rs
    ├── capabilities/default.json
    └── build.ps1
```

---

## Implementation Phases (8)

### Phase 1: Scaffold & Config
- `pyproject.toml` (hatchling + uv-dynamic-versioning, all deps)
- `justfile` (full fleet standard: install, start, webapp, lint, fix, fmt, test, ci, clean, build-*)
- `.env.example` with all 7 arr config sections
- `.pre-commit-config.yaml` (ruff, biome, etc.)
- `.github/workflows/ci.yml`
- `src/arr_mcp/__init__.py`, `__main__.py`, `config.py`
- `ArrConfig` Pydantic model with sub-configs — each independently optional

### Phase 2: Base Client Library
- `src/arr_mcp/services/base.py` — `BaseArrClient` with:
  - Shared methods: `get_health()`, `get_system_status()`, `get_queue()`, `get_history()`, `get_calendar()`, `get_commands()`, `trigger_command(name)`, `get_diskspace()`, `get_logs()`, `get_backups()`, `get_tags()`
  - Paging support: `get_all(endpoint, **params)` with auto-pagination
  - Auth injection: `X-Api-Key` header (or `apikey` query param for Lidarr/Readarr)
- Pydantic models in `models/common.py`: `HealthCheck`, `QueueItem`, `HistoryItem`, `CommandItem`, `DiskSpace`, `Backup`, `Tag`, `SystemStatus`

### Phase 3: Radarr Tools
- `services/radarr.py`: `RadarrClient(BaseArrClient)` — movies, lookup, wanted, indexers
- `tools/portmanteau/radarr.py`: `radarr_media(operation: Literal[...])` ~15 operations
- Tests: mocked httpx for each operation

### Phase 4: Sonarr Tools
- `services/sonarr.py`: `SonarrClient(BaseArrClient)` — series, episodes, lookup
- `tools/portmanteau/sonarr.py`: `sonarr_media(operation: Literal[...])` ~15 operations
- Tests: unit tests

### Phase 5: Lidarr Tools
- `services/lidarr.py`: `LidarrClient(BaseArrClient)` — artists, albums, tracks, v1 API
- `tools/portmanteau/lidarr.py`: `lidarr_media(operation: Literal[...])` ~12 operations
- Tests: unit tests

### Phase 6: Prowlarr + Bazarr + Readarr
- **Prowlarr**: Indexer management, unified search, application sync, stats
- **Bazarr**: Separate base client, subtitle management, system status
- **Readarr**: DEPRECATED — Books and authors, last-version API, deprecation warnings
- Tests: unit tests for all three

### Phase 7: Cross-Orchestration & Health (THE DIFFERENTIATOR)
- **Health check**: `arr_stack_health()` — matrix of all configured arrs
- **Jellyfin bridge**: `check_availability(title, type)` — HTTP search in Jellyfin
- **Orchestrator**: `arr_orchestrate(search_and_add)` — check Jellyfin → route to correct arr
- This is the killer feature — no other tool does Jellyfin cross-referencing

### Phase 8: Webapp, CI, Packaging
- **Webapp backend** (FastAPI, port 10982): API endpoints for each arr
- **Webapp frontend** (Next.js 15.2, port 10983): Dashboard with arr tabs, orchestration panel
- **GitHub Actions**: ci, release, industrial-launch, version-bump
- **DXT packaging + Tauri 2.0 native**: Tauri + PyInstaller sidecar
- **README, CHANGELOG, AGENTS.md**

---

## Conditional Tool Registration

```python
# tools/__init__.py pseudocode
def register_tools(mcp, config):
    if config.radarr.enabled:
        from .portmanteau import radarr
    if config.sonarr.enabled:
        from .portmanteau import sonarr
    if config.lidarr.enabled:
        from .portmanteau import lidarr
    if config.prowlarr.enabled:
        from .portmanteau import prowlarr
    if config.bazarr.enabled:
        from .portmanteau import bazarr
    if config.readarr.enabled:
        from .portmanteau import readarr  # emits deprecation warning

    # Always register (they adapt to whatever is configured)
    from .portmanteau import health
    if config.jellyfin.enabled:
        from .portmanteau import orchestrate
    from .portmanteau import help
    from .portmanteau import reporting
```

---

## .env.example

```bash
# Radarr (Movies)
RADARR_URL=http://localhost:7878
RADARR_API_KEY=

# Sonarr (TV Series)
SONARR_URL=http://localhost:8989
SONARR_API_KEY=

# Lidarr (Music)
LIDARR_URL=http://localhost:8686
LIDARR_API_KEY=

# Prowlarr (Indexers)
PROWLARR_URL=http://localhost:9696
PROWLARR_API_KEY=

# Bazarr (Subtitles)
BAZARR_URL=http://localhost:6767
BAZARR_API_KEY=

# Readarr (Books — DEPRECATED: project archived June 2025)
# READARR_URL=http://localhost:8787
# READARR_API_KEY=

# Jellyfin (for cross-arr orchestration)
JELLYFIN_URL=http://localhost:8096
JELLYFIN_API_KEY=

# Transport
ARR_MCP_TRANSPORT=stdio
ARR_MCP_PORT=10982
```

---

## Dependency Matrix

```toml
dependencies = [
    "fastmcp>=3.2.0",
    "prefab-ui>=0.18.0",
    "httpx>=0.28.0",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
    "rich>=13.0.0",
    "aiohttp>=3.9.0",
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "python-multipart>=0.0.6",
    "lancedb>=0.4.0",
    "sentence-transformers>=2.2.0",
    "ruff>=0.14.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.24.0",
    "pytest-cov>=5.0.0",
    "pytest-httpx>=0.30.0",
    "mypy>=1.8.0",
    "pre-commit>=3.6.0",
]
```

**NO external arr Python client libraries** — the APIs are thin REST JSON wrappers. A 250-line `BaseArrClient` with httpx replaces any third-party library.

---

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| **API drift across *arr versions** | Each client reports version on connect; warn if >1 major version behind |
| **Readarr dead, users still run it** | Flag as deprecated, still function, point to alternatives |
| **Bazarr API differs significantly** | Separate BaseBazarrClient, no coupling to Servarr base |
| **Jellyfin search accuracy** | Fuzzy matching + year comparison; gate behind `JELLYFIN_URL` config |
| **Cross-arr orchestration adding wrong media** | Confirmation step: lookup first, explicit `add` operation |

---

## Differentiating Features

1. **Cross-arr orchestration with Jellyfin bridge** — no other tool checks Jellyfin before queuing
2. **Conditional tool registration** — Lidarr not running? Those tools don't exist
3. **Unified health dashboard** — one tool shows the entire stack
4. **Prowlarr as backbone** — unified search, not per-arr indexer management
5. **Bazarr subtitle bridge** — feeds jellyfin-mcp RAG pipeline downstream
6. **Readarr deprecation handling** — honest about the project's death, functional for existing users
