# arr-mcp — Implementation Plan

> FastMCP 3.2.4+ server for the complete *arr automation stack.
> **Status: PLAN (pending approval)**

---

## 0. Research Summary

### 0.1 *arr API Landscape (May 2026)

All *arr apps (except Bazarr) share a common .NET base, forked from Sonarr:

| App | Default Port | API Base | Version | Key ID Schema |
|---|---|---|---|---|
| **Sonarr** | 8989 | `/api/v3` | v3 (stable, also used by v4) | `seriesId` |
| **Radarr** | 7878 | `/api/v3` | v3 (Radarr v6 uses v3 API) | `movieId` |
| **Lidarr** | 8686 | `/api/v1` | v1 (Lidarr v2) | `artistId` |
| **Prowlarr** | 9696 | `/api/v1` | v1 (Prowlarr v2) | `indexerId` |
| **Readarr** | 8787 | `/api/v1` | v1 (Readarr v0.4) | `bookId` |
| **Bazarr** | 6767 | `/api` | REST (Python, not Servarr) | `seriesId`, `episodeId` |

**Auth**: All Servarr apps use `X-Api-Key` header. Bazarr also uses `X-Api-Key`.

**Common endpoints (~60% shared)**:
- `GET /api/v{1|3}/system/status` — health
- `GET /api/v{1|3}/health` — health checks
- `GET /api/v{1|3}/queue` — download queue
- `GET /api/v{1|3}/history` — history
- `GET /api/v{1|3}/log` — logs
- `GET /api/v{1|3}/command` — commands
- `GET /api/v{1|3}/diskspace` — disk space

**Unique endpoints**:
- Radarr: `GET /api/v3/movie`, `POST /api/v3/movie` — movies
- Sonarr: `GET /api/v3/series`, `GET /api/v3/episode` — TV
- Lidarr: `GET /api/v1/artist`, `GET /api/v1/album` — music
- Readarr: `GET /api/v1/book`, `GET /api/v1/author` — books
- Prowlarr: `GET /api/v1/search`, `GET /api/v1/indexer` — search/indexers
- Bazarr: `GET /api/episodes`, `POST /api/webhooks` — subtitles

### 0.2 Fleet Patterns (jellyfin-mcp, plex-mcp, calibre-mcp)

| Aspect | Convention |
|---|---|
| **Build system** | hatchling + `uv-dynamic-versioning` (pep440 from git tags) |
| **Package layout** | `src/<repo>_mcp/` (src-layout) |
| **FastMCP pin** | `fastmcp>=3.2.0` |
| **Python** | `>=3.12` |
| **Tool registration** | `@mcp.tool()` decorator at import time via portmanteau `__init__.py` |
| **Config** | Pydantic v2 `BaseSettings` + `python-dotenv` |
| **Transport** | Dual stdio/HTTP via `transport.py` |
| **Ruff** | `line-length=120`, double quotes, space indent, py312 target |
| **Biome** | v1.9.4, organized imports, single quotes, trailing commas |
| **Justfile** | 23+ recipes: `default`, `install`, `start`, `webapp`, `lint`, `fix`, `fmt`, `test`, `ci`, `clean` |
| **CI** | `.github/workflows/ci.yml` (lint + typecheck + test + server-import) |
| **.env.example** | Simple KEY=value with comments |
| **README** | Badges → quickstart → Claude config → docs table → ports → tech stack |
| **CHANGELOG** | Keep a Changelog format |

---

## Phase 1: Scaffold & Tooling (no code, just config)

**Goal**: Empty repo skeleton matching fleet conventions.

### 1.1 Python project
- `pyproject.toml`: hatchling build, `fastmcp>=3.2.0`, `httpx>=0.27.0`, ruff config
- `justfile`: all standard recipes
- `.env.example`: all *arr config vars (one per app, optional)
- `.gitignore`: Python + ruff + venv + IDE
- `.python-version`: `3.12`

### 1.2 Quality tooling
- Ruff config in `pyproject.toml`
- `.pre-commit-config.yaml` (ruff + mypy + bandit)
- `AGENTS.md`

### 1.3 CI/CD
- `.github/workflows/ci.yml`: lint → typecheck → test → server-import
- No release workflow yet (v0.1)

### Deliverables
```
arr-mcp/
├── pyproject.toml
├── justfile
├── .env.example
├── .gitignore
├── .python-version
├── .pre-commit-config.yaml
├── AGENTS.md
├── .github/workflows/ci.yml
└── README.md (stub)
```

---

## Phase 2: Core Configuration & Shared Client

**Goal**: Pydantic config models + shared `ArrClient` base class.

### 2.1 Configuration (`src/arr_mcp/config.py`)

```python
class ArrConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="", env_file=".env")
    
    # Per-app configs — all optional
    sonarr_url: str | None      # e.g. http://localhost:8989
    sonarr_api_key: str | None
    radarr_url: str | None
    radarr_api_key: str | None
    lidarr_url: str | None
    lidarr_api_key: str | None
    prowlarr_url: str | None
    prowlarr_api_key: str | None
    readarr_url: str | None
    readarr_api_key: str | None
    bazarr_url: str | None
    bazarr_api_key: str | None
    
    # Cross-arr integration
    jellyfin_url: str | None    # For Jellyfin availability check
    jellyfin_api_key: str | None
    
    # Server settings
    arr_mcp_transport: Literal["stdio", "http", "sse"] = "stdio"
    arr_mcp_port: int = 10936
    
    # Timeout for all HTTP calls
    timeout: int = 30
```

### 2.2 Shared Base Client (`src/arr_mcp/clients/base.py`)

All *arr apps share ~60% of their API surface. One base class:

```python
class ArrBaseClient:
    """Shared HTTP client for Servarr-based apps (Sonarr/Radarr/Lidarr/Readarr)."""
    
    def __init__(self, base_url: str, api_key: str, api_version: str = "v3", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.api_version = api_version
        self.timeout = timeout
    
    # === Shared methods (common to all *arr apps) ===
    
    async def get_system_status(self) -> dict
    async def get_health(self) -> list[dict]
    async def get_queue(self, **params) -> dict          # download queue
    async def get_history(self, **params) -> dict        # history
    async def get_logs(self, **params) -> dict
    async def get_commands(self) -> list[dict]
    async def run_command(self, name: str, **kwargs) -> dict
    async def get_diskspace(self) -> list[dict]
    async def get_blocklist(self, **params) -> dict
    async def delete_blocklist_item(self, id: int) -> None
```

### 2.3 Per-App Clients (thin wrappers)

Each client extends `ArrBaseClient` and adds only the app-specific methods:

```python
# src/arr_mcp/clients/sonarr_client.py
class SonarrClient(ArrBaseClient):
    api_version = "v3"
    
    async def get_series(self, **params) -> list[dict]
    async def get_series_by_id(self, id: int) -> dict
    async def add_series(self, data: dict) -> dict
    async def get_episodes(self, series_id: int, **params) -> list[dict]
    async def get_calendar(self, **params) -> list[dict]
    async def get_wanted(self, **params) -> dict
    async def trigger_series_search(self, id: int) -> None
    async def trigger_episode_search(self, id: int) -> None

# src/arr_mcp/clients/radarr_client.py
class RadarrClient(ArrBaseClient):
    api_version = "v3"
    
    async def get_movies(self, **params) -> list[dict]
    async def get_movie_by_id(self, id: int) -> dict
    async def add_movie(self, data: dict) -> dict
    async def get_calendar(self, **params) -> list[dict]
    async def get_wanted(self, **params) -> dict
    async def trigger_movie_search(self, id: int) -> None
    async def lookup_movie(self, term: str) -> list[dict]    # Radarr lookup via Skyhook

# src/arr_mcp/clients/lidarr_client.py
class LidarrClient(ArrBaseClient):
    api_version = "v1"
    
    async def get_artists(self, **params) -> list[dict]
    async def get_artist_by_id(self, id: int) -> dict
    async def add_artist(self, data: dict) -> dict
    async def get_albums(self, artist_id: int) -> list[dict]
    async def get_wanted(self, **params) -> dict
    async def trigger_artist_search(self, id: int) -> None

# src/arr_mcp/clients/readarr_client.py
class ReadarrClient(ArrBaseClient):
    api_version = "v1"
    
    async def get_books(self, **params) -> list[dict]
    async def get_book_by_id(self, id: int) -> dict
    async def get_authors(self, **params) -> list[dict]
    async def add_book(self, data: dict) -> dict
    async def get_wanted(self, **params) -> dict
    async def trigger_book_search(self, id: int) -> None

# src/arr_mcp/clients/prowlarr_client.py
class ProwlarrClient(ArrBaseClient):
    api_version = "v1"
    
    async def get_indexers(self) -> list[dict]
    async def get_indexer_stats(self) -> dict
    async def search(self, query: str, **params) -> list[dict]
    async def get_apps(self) -> list[dict]                       # connected *arr apps
    async def sync_indexers(self) -> dict                        # push indexers to apps
    async def get_notifications(self) -> list[dict]
    async def test_indexer(self, id: int) -> dict

# src/arr_mcp/clients/bazarr_client.py
class BazarrClient(ArrBaseClient):
    api_version = ""  # Bazarr is Python, different API
    
    async def get_system_status(self) -> dict
    async def get_episodes(self, **params) -> list[dict]
    async def get_wanted(self, **params) -> list[dict]
    async def get_history(self, **params) -> list[dict]
    async def search_subtitles(self, series_id: int, episode_id: int, **params) -> list[dict]
    async def download_subtitle(self, **params) -> dict
    async def get_providers(self) -> list[dict]
    async def get_languages(self) -> list[dict]
```

### 2.4 Client Factory (`src/arr_mcp/clients/__init__.py`)

Conditional client creation — only instantiate what's configured:

```python
def get_available_clients(config: ArrConfig) -> dict[str, ArrBaseClient]:
    """Return dict of {app_name: client} for configured apps only."""
    clients = {}
    for app_name in ["sonarr", "radarr", "lidarr", "prowlarr", "readarr", "bazarr"]:
        url = getattr(config, f"{app_name}_url", None)
        key = getattr(config, f"{app_name}_api_key", None)
        if url and key:
            clients[app_name] = CLIENT_CLASSES[app_name](url, key, config.timeout)
    return clients
```

### Deliverables
```
src/arr_mcp/
├── __init__.py
├── __main__.py
├── config.py
├── transport.py
└── clients/
    ├── __init__.py          # Factory + exports
    ├── base.py              # ArrBaseClient
    ├── sonarr_client.py
    ├── radarr_client.py
    ├── lidarr_client.py
    ├── readarr_client.py
    ├── prowlarr_client.py
    └── bazarr_client.py
```

---

## Phase 3: FastMCP Server & Tool Registration Framework

**Goal**: FastMCP instance, portmanteau import pattern, transport layer.

### 3.1 Server (`src/arr_mcp/server.py`)

```python
from fastmcp import FastMCP

mcp = FastMCP(
    "ArrMCP",
    instructions="""You are an AI assistant with full access to the *arr media automation stack.
    You can check the status of Sonarr, Radarr, Lidarr, Prowlarr, Readarr, and Bazarr.
    You can search for and add media, check download queues, and trigger searches.
    Cross-arr orchestration: check Jellyfin availability before queuing content.""",
    on_duplicate="replace",
    strict_input_validation=True,
)

# Tool registration via portmanteau imports
# Each module imports 'mcp' and uses @mcp.tool()

def main():
    from .transport import run_server
    from .tools import portmanteau  # noqa: F401 — triggers all @mcp.tool() registrations
    run_server(mcp, server_name="arr-mcp")
```

### 3.2 Transport (`src/arr_mcp/transport.py`)

Dual stdio/HTTP transport matching jellyfin-mcp pattern:
- stdio: default for Claude Desktop
- http: for webapp backend to mount as ASGI
- sse: for streaming events

### 3.3 Tool Registration Framework

Portmanteau pattern — each tool file:
1. Imports `mcp` from `...server`
2. Uses `@mcp.tool(version="1.0.0", annotations={...})` decorator
3. Operates as a portmanteau with `operation: Literal[...]` parameter
4. Returns `ToolResult(content={"success": bool, "data": ..., "operation": str})`

### Deliverables
```
src/arr_mcp/
├── server.py
├── transport.py
├── app.py                  # FastMCP instance factory
├── tools/
│   ├── __init__.py         # from . import portmanteau
│   └── portmanteau/
│       ├── __init__.py     # Re-exports all tool functions
│       ├── sonarr_tools.py
│       ├── radarr_tools.py
│       ├── lidarr_tools.py
│       ├── readarr_tools.py
│       ├── prowlarr_tools.py
│       ├── bazarr_tools.py
│       ├── health.py       # Stack-wide health check
│       ├── orchestration.py # Cross-arr orchestration
│       └── help.py         # Tool discovery
```

---

## Phase 4: Per-App Tool Modules

**Goal**: One portmanteau tool per *arr app. Each handles multiple operations.

### 4.1 Tool Design Principle

Each tool is a single portmanteau with an `operation` literal parameter:

```python
@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True, "destructiveHint": False})
async def arr_radarr(
    operation: Annotated[Literal["status", "list", "get", "search", "add", "delete", "queue", "history", "calendar", "wanted", "lookup", "trigger_search", "refresh"], Field(description="Operation to perform.")],
    ...
) -> ToolResult:
```

### 4.2 Tool Breakdown

| Tool | Module | Operations | ReadOnly? |
|---|---|---|---|
| `arr_sonarr` | `sonarr_tools.py` | status, list, get, search, add, delete, queue, history, calendar, wanted, trigger_search, trigger_episode_search, refresh | Mostly |
| `arr_radarr` | `radarr_tools.py` | status, list, get, search, add, delete, queue, history, calendar, wanted, lookup, trigger_search, refresh | Mostly |
| `arr_lidarr` | `lidarr_tools.py` | status, list, get, search, add, delete, queue, history, wanted, trigger_search, refresh | Mostly |
| `arr_readarr` | `readarr_tools.py` | status, list, get, search, add, delete, queue, history, wanted, trigger_search, refresh | Mostly |
| `arr_prowlarr` | `prowlarr_tools.py` | status, indexers, search, apps, sync, history, stats, notifications, test_indexer | Mostly |
| `arr_bazarr` | `bazarr_tools.py` | status, episodes, wanted, history, search_subtitles, download, providers, languages | Mostly |

### 4.3 Conditional Tool Registration

If an *arr is not configured, its tool is simply not imported:

```python
# In portmanteau/__init__.py:
from ..config import get_config
config = get_config()

if config.sonarr_url and config.sonarr_api_key:
    from .sonarr_tools import arr_sonarr  # noqa: F401

if config.radarr_url and config.radarr_api_key:
    from .radarr_tools import arr_radarr  # noqa: F401
# ... etc
```

### Deliverables
```
src/arr_mcp/tools/portmanteau/
├── __init__.py
├── sonarr_tools.py         (300-400 lines)
├── radarr_tools.py         (300-400 lines)
├── lidarr_tools.py         (250-350 lines)
├── readarr_tools.py        (250-350 lines)
├── prowlarr_tools.py       (350-450 lines)
└── bazarr_tools.py         (250-350 lines)
```

---

## Phase 5: Health Check & Cross-arr Orchestration

**Goal**: Differentiating features — health dashboard + Jellyfin bridge.

### 5.1 Stack Health Check (`health.py`)

```python
@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True, "destructiveHint": False})
async def arr_health() -> ToolResult:
    """Check health of all configured *arr services.
    
    Returns status for each configured app:
    - online/offline
    - version
    - disk space
    - queue size
    - health check results (warnings/errors)
    """
```

### 5.2 Cross-arr Orchestration (`orchestration.py`)

**This is the killer feature.** The cross-arr orchestration tool with Jellyfin availability bridge.

```python
@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": True})
async def arr_orchestrate(
    title: Annotated[str, Field(description="Media title to search for.")],
    media_type: Annotated[Literal["movie", "series", "artist", "book"], Field(description="Type of media.")] = "movie",
    check_jellyfin: Annotated[bool, Field(description="Check Jellyfin first before queuing.")] = True,
    queue_if_missing: Annotated[bool, Field(description="Queue in the appropriate arr if not found.")] = True,
) -> ToolResult:
    """Cross-arr orchestration with Jellyfin bridge.
    
    Flow:
    1. If check_jellyfin and Jellyfin is configured:
       a. Search Jellyfin for the title
       b. If found → return "Already available in Jellyfin"
       c. If not found → continue to step 2
    2. Determine the appropriate *arr based on media_type:
       - movie → Radarr
       - series → Sonarr
       - artist → Lidarr
       - book → Readarr
    3. If queue_if_missing:
       a. Lookup the title in the appropriate *arr
       b. If found → return status
       c. If not found → add and trigger search
    4. Return orchestration summary
    
    ## Return Format
    {
        "success": bool,
        "jellyfin_available": bool | None,
        "action": "found_in_jellyfin" | "already_queued" | "queued" | "not_configured",
        "arr_used": str | None,
        "details": dict
    }
    """
```

### 5.3 Prowlarr Cross-Search

```python
@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True, "destructiveHint": False})
async def arr_prowlarr_cross_search(
    query: Annotated[str, Field(description="Search query for TV/movie/music/book content.")],
    categories: Annotated[list[int], Field(description="Prowlarr category IDs.")] = None,
) -> ToolResult:
    """Search across all trackers and indexers via Prowlarr."""
```

### Deliverables
```
src/arr_mcp/tools/portmanteau/
├── health.py
└── orchestration.py
```

---

## Phase 6: Webapp Backend (REST API)

**Goal**: FastAPI backend that mounts the MCP server and provides REST endpoints for a dashboard.

### 6.1 Architecture
```
Browser → localhost:10937 (Next.js) → /api/* → localhost:10936 (FastAPI)
                                    → /mcp  → FastMCP HTTP endpoints
```

### 6.2 Backend (`webapp/backend/app/main.py`)

Lazy MCP mount pattern (matching jellyfin-mcp/plex-mcp):
- FastAPI app on port 10936
- CORS middleware
- `/health` endpoint
- `/mcp` mount for FastMCP HTTP
- REST routes for dashboard views

### 6.3 API Routes

| Route | Purpose |
|---|---|
| `GET /api/status` | All *arr health status |
| `GET /api/{app}/queue` | Download queue per app |
| `GET /api/{app}/calendar` | Upcoming releases |
| `GET /api/{app}/wanted` | Missing content |
| `GET /api/prowlarr/search` | Cross-indexer search |

### 6.4 Port Assignment

| Port | Service |
|---|---|
| 10936 | arr-mcp Backend (FastAPI + MCP HTTP) |
| 10937 | arr-mcp Frontend (Next.js) |

From WEBAPP_PORTS.md: 10936-10939 are available (next after godot-mcp 10993/10992, before freecad-mcp 10944/10945 — moving earlier into the gap).

### Deliverables
```
webapp/
├── start.ps1
├── start.bat
├── backend/
│   ├── env.example
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── config.py
│       └── api/
│           ├── __init__.py
│           ├── status.py
│           ├── queue.py
│           ├── calendar.py
│           └── search.py
└── frontend/                    (Phase 7)
```

---

## Phase 7: Webapp Frontend (React Dashboard)

**Goal**: Next.js 15.2 dashboard for the *arr stack.

### 7.1 Tech Stack
- Next.js 15.2 (React 18)
- Tailwind CSS 3.4
- Biome 1.9.4
- TypeScript
- Playwright for E2E

### 7.2 Pages

| Route | Purpose |
|---|---|
| `/` | Overview dashboard — all *arr health cards |
| `/radarr` | Movies list + add/search |
| `/sonarr` | Series list + add/search |
| `/lidarr` | Artists/albums list |
| `/readarr` | Books list |
| `/prowlarr` | Indexer management + cross-search |
| `/bazarr` | Subtitle history + wanted |
| `/queue` | Unified download queue |
| `/calendar` | Unified calendar |
| `/orchestrate` | Cross-arr orchestration UI |
| `/health` | Stack health dashboard |
| `/help` | Tool catalog |

### 7.3 Key Components
- `StackHealthCard`: Shows online/offline, version, queue count per app
- `QueueWidget`: Real-time download progress
- `CalendarWidget`: Upcoming releases
- `OrchestratePanel`: Search Jellyfin → queue in arr UI flow
- `CrossSearchWidget`: Prowlarr search with per-app results

### Deliverables
```
webapp/frontend/
├── package.json
├── biome.json
├── next.config.js
├── tsconfig.json
├── tailwind.config.ts
├── playwright.config.ts
├── app/
│   ├── layout.tsx
│   ├── globals.css
│   ├── page.tsx
│   ├── radarr/page.tsx
│   ├── sonarr/page.tsx
│   ├── lidarr/page.tsx
│   ├── readarr/page.tsx
│   ├── prowlarr/page.tsx
│   ├── bazarr/page.tsx
│   ├── queue/page.tsx
│   ├── calendar/page.tsx
│   ├── orchestrate/page.tsx
│   ├── health/page.tsx
│   └── help/page.tsx
├── components/
│   └── layout/
│       ├── app-layout.tsx
│       └── sidebar.tsx
└── utils/
    └── api.ts
```

---

## Phase 8: Documentation, CI Polish & Release

**Goal**: README, CHANGELOG, CI hardening, Claude Desktop config.

### 8.1 Documentation
- `README.md`: Full project readme (badges, quickstart, Claude config, docs table, ports, tech stack)
- `CHANGELOG.md`: Keep a Changelog format, v0.1.0 initial
- `docs/`: Optional — kept minimal for v0.1

### 8.2 CI Hardening
- `ci.yml`: lint + typecheck + test + server-import
- Test matrix: Python 3.12 + 3.13
- Codecov upload
- Optional: linkcheck (lychee)
- Optional: Playwright E2E (headless)

### 8.3 Claude Desktop Config
```json
{
  "mcpServers": {
    "arr-mcp": {
      "command": "uv",
      "args": ["run", "arr-mcp"],
      "env": {
        "SONARR_URL": "http://localhost:8989",
        "SONARR_API_KEY": "your-key",
        "RADARR_URL": "http://localhost:7878",
        "RADARR_API_KEY": "your-key",
        "JELLYFIN_URL": "http://localhost:8096",
        "JELLYFIN_API_KEY": "your-jellyfin-key"
      }
    }
  }
}
```

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────┐
│                     arr-mcp (10936)                       │
│  ┌──────────────────────────────────────────────────┐   │
│  │              FastMCP 3.2 Server                    │   │
│  │  ┌──────────┐ ┌─────────┐ ┌──────────────────┐   │   │
│  │  │ Sonarr   │ │ Radarr  │ │ Prowlarr (index) │   │   │
│  │  │ Tools    │ │ Tools   │ │ Tools            │   │   │
│  │  ├──────────┤ ├─────────┤ ├──────────────────┤   │   │
│  │  │ Lidarr   │ │ Readarr │ │ Bazarr (subs)    │   │   │
│  │  │ Tools    │ │ Tools   │ │ Tools            │   │   │
│  │  └──────────┘ └─────────┘ └──────────────────┘   │   │
│  │  ┌──────────────────────────────────────────┐     │   │
│  │  │     Cross-arr Orchestration + Health      │     │   │
│  │  └──────────────────────────────────────────┘     │   │
│  └──────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Shared Base Client                    │   │
│  │  (httpx.AsyncClient + X-Api-Key auth)             │   │
│  └──────────────────────────────────────────────────┘   │
└──────────┬──────────┬──────────┬──────────┬────────────┘
           │          │          │          │
    ┌──────▼──┐ ┌────▼───┐ ┌───▼───┐ ┌───▼───┐
    │ Sonarr  │ │ Radarr │ │Prowlarr│ │Jellyfin│
    │ :8989   │ │ :7878  │ │ :9696  │ │ :8096  │
    └─────────┘ └────────┘ └───────┘ └────────┘

           Webapp:
    ┌─────────────────────────────────────┐
    │  Next.js :10937  →  FastAPI :10936  │
    │  /api/* proxy   →  REST + /mcp      │
    └─────────────────────────────────────┘
```

## Summary

| Phase | What | Lines (est.) | Files |
|---|---|---|---|
| 1 | Scaffold & Tooling | ~200 | 8 |
| 2 | Core Config & Clients | ~1200 | 10 |
| 3 | Server & Tool Framework | ~400 | 5 |
| 4 | Per-App Tool Modules | ~2000 | 7 |
| 5 | Health & Orchestration | ~500 | 3 |
| 6 | Webapp Backend | ~600 | 8 |
| 7 | Webapp Frontend | ~2000 | 20+ |
| 8 | Docs & CI Polish | ~300 | 5 |

**Total estimated**: ~7200 lines, ~66 files.

---

*Awaiting approval before Phase 1 implementation.*
