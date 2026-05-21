# arr-mcp — Implementation Plan

**FastMCP 3.2.4+ Python MCP server for the complete *arr automation stack.**

| Field | Value |
|-------|-------|
| Package | `schip-mcp-arr` v0.1.0 |
| Repo | `sandraschi/arr-mcp` |
| Ports | 10856 (backend) / 10857 (frontend) |
| Python | >=3.12 |
| Dependencies | fastmcp>=3.2.0, httpx>=0.25.0, pydantic>=2.0.0, pydantic-settings, python-dotenv, fastapi, uvicorn |
| Build | hatchling + uv-dynamic-versioning |
| Lint | Ruff (line-length=120, py312, fleet select/ignore), Biome (webapp) |
| CI | GitHub Actions: lint → test → e2e |

---

## Phase 1: Repo Scaffolding

### 1.1 Directory Structure

```
arr-mcp/
├── .env.example
├── .gitignore
├── .python-version
├── CHANGELOG.md
├── README.md
├── justfile
├── pyproject.toml
├── run_server.py              # PyInstaller entry (future Tauri)
├── start.ps1                  # Root-level launcher
├── uv.lock
├── .github/
│   └── workflows/
│       └── ci.yml
├── src/
│   └── arr_mcp/
│       ├── __init__.py
│       ├── __main__.py         # → from .server import main; main()
│       ├── app.py              # FastMCP instance, lifespan, resources, prompts, http_app()
│       ├── config.py           # ArrConfig pydantic model (all env vars, per-service optional)
│       ├── server.py           # main(), imports portmanteau, registers agentic, builds Starlette
│       ├── transport.py        # Unified transport (stdio/http/sse) — copy from jellyfin-mcp
│       ├── models/
│       │   ├── __init__.py     # Re-exports all models
│       │   ├── common.py       # Shared Pydantic models (Movie, Series, Episode, Artist, Album, Book, etc.)
│       │   ├── radarr.py       # Radarr-specific models (MovieResource, QualityProfile, etc.)
│       │   ├── sonarr.py       # Sonarr-specific models
│       │   ├── lidarr.py
│       │   ├── readarr.py
│       │   └── prowlarr.py     # Prowlarr-specific (IndexerResource, AppProfile, etc.)
│       ├── services/
│       │   ├── __init__.py
│       │   ├── base.py         # BaseService(ABC), ServiceError, AuthenticationError, ConnectionError, NotFoundError
│       │   ├── arr_client.py   # ArrClient — shared httpx wrapper for Servarr API (~60% shared surface)
│       │   ├── radarr.py       # RadarrService(ArrClient)
│       │   ├── sonarr.py       # SonarrService(ArrClient)
│       │   ├── lidarr.py       # LidarrService(ArrClient)
│       │   ├── readarr.py      # ReadarrService(ArrClient)
│       │   ├── prowlarr.py     # ProwlarrService(ArrClient) — indexer management
│       │   ├── bazarr.py       # BazarrService(httpx.AsyncClient) — standalone, not Servarr-derived
│       │   └── jellyfin.py     # JellyfinBridge — HTTP availability check (optional dep)
│       ├── tools/
│       │   ├── __init__.py     # Re-exports all portmanteau tools
│       │   ├── agentic.py      # register_agentic_arr_tools(mcp) — cross-arr orchestration
│       │   ├── portmanteau/
│       │   │   ├── __init__.py # Portmanteau re-exports
│       │   │   ├── radarr.py   # arr_radarr tool (add, search, delete, queue, history, quality, rootfolder, import_list, calendar)
│       │   │   ├── sonarr.py   # arr_sonarr tool
│       │   │   ├── lidarr.py   # arr_lidarr tool
│       │   │   ├── readarr.py  # arr_readarr tool
│       │   │   ├── prowlarr.py # arr_prowlarr tool (indexer CRUD, search, application sync, stats)
│       │   │   ├── bazarr.py   # arr_bazarr tool (subtitle search, download, history, providers, languages)
│       │   │   ├── health.py   # arr_health tool (check all services, individual health probes)
│       │   │   ├── orchestrator.py # arr_orchestrate — cross-arr: check Jellyfin → queue media
│       │   │   └── help.py     # arr_help tool (discover all tools, operations, ports, quickstart)
│       │   └── utils.py        # Tool helpers (get_service factories)
│       ├── utils/
│       │   ├── __init__.py
│       │   └── logging.py      # get_logger using NullLogger for stdio
│       └── webapp/             # (Phase 8)
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Fixtures: mock ArrClient, mock httpx responses
│   ├── test_radarr_tools.py
│   ├── test_sonarr_tools.py
│   ├── test_lidarr_tools.py
│   ├── test_readarr_tools.py
│   ├── test_prowlarr_tools.py
│   ├── test_bazarr_tools.py
│   ├── test_health.py
│   └── test_orchestrator.py
└── webapp/                     # (Phase 8 — React dashboard)
```

### 1.2 Port Allocation

| Port | Service |
|------|---------|
| 10856 | arr-mcp Backend (FastAPI + FastMCP HTTP `/mcp`) |
| 10857 | arr-mcp Frontend (Vite React dashboard) |

Verified unallocated in both `WEBAPP_PORTS.md` and `webapp-registry.json`.

---

## Phase 2: Configuration Layer (`config.py`)

### 2.1 ArrConfig Pydantic Model

```python
class ArrConfig(BaseModel):
    # Transport
    mcp_transport: str = "stdio"
    mcp_port: int = 10856

    # Radarr
    radarr_url: str | None = None        # http://localhost:7878
    radarr_api_key: str | None = None
    radarr_enabled: bool = False          # Disabled by default → tools don't register

    # Sonarr
    sonarr_url: str | None = None         # http://localhost:8989
    sonarr_api_key: str | None = None
    sonarr_enabled: bool = False

    # Lidarr
    lidarr_url: str | None = None         # http://localhost:8686
    lidarr_api_key: str | None = None
    lidarr_enabled: bool = False

    # Readarr
    readarr_url: str | None = None        # http://localhost:8787
    readarr_api_key: str | None = None
    readarr_enabled: bool = False

    # Prowlarr
    prowlarr_url: str | None = None       # http://localhost:9696
    prowlarr_api_key: str | None = None
    prowlarr_enabled: bool = False

    # Bazarr
    bazarr_url: str | None = None         # http://localhost:6767
    bazarr_api_key: str | None = None
    bazarr_enabled: bool = False

    # Jellyfin bridge (cross-arr orchestration)
    jellyfin_url: str | None = None       # http://localhost:8096
    jellyfin_api_key: str | None = None   # Optional but unlocks orchestration
    jellyfin_enabled: bool = False

    # Shared
    timeout: int = 30
```

**Key invariant**: tools only register if `*_enabled=True` and the service responds to a health probe during server boot. This matches the jellyfin-mcp lifespan pattern.

---

## Phase 3: Shared Base Client (`services/arr_client.py`)

### 3.1 Servarr API Compatibility Matrix

The 5 Servarr-based apps (Radarr, Sonarr, Lidarr, Readarr, Prowlarr) share:
- Auth: `X-Api-Key` header
- Pagination: same query params
- Error format: `{message: string}`
- Health: `GET /health` → 200
- System status: `GET /api/v{1,3}/system/status`
- Disk space: `GET /api/v{1,3}/diskspace`
- Queue: `GET /api/v{1,3}/queue` (with optional params)
- History: `GET /api/v{1,3}/history`
- Calendar: `GET /api/v{1,3}/calendar`
- Wanted: `GET /api/v{1,3}/wanted/missing`
- Commands: `POST /api/v{1,3}/command` (trigger refresh, rescan, rss sync)
- Tags, root folders, quality profiles, import lists, notifications, download clients

**API version differences:**
| App | Version | Base Path | Entity Endpoint |
|-----|---------|-----------|-----------------|
| Radarr | v3 | `/api/v3/` | `/movie`, `/movie/lookup` |
| Sonarr | v3/v4 | `/api/v3/` | `/series`, `/series/lookup`, `/episode` |
| Lidarr | v1 | `/api/v1/` | `/artist`, `/artist/lookup`, `/album` |
| Readarr | v1 | `/api/v1/` | `/author`, `/author/lookup`, `/book` |
| Prowlarr | v1 | `/api/v1/` | `/indexer`, `/appprofile`, `/applications` |

### 3.2 ArrClient Design

```python
class ArrClient:
    """Shared httpx-based REST client for all Servarr-compatible *arr apps.

    Handles: X-Api-Key auth, pagination, error wrapping, rate limiting.
    Derived services: RadarrService, SonarrService, LidarrService, ReadarrService, ProwlarrService.
    """

    def __init__(self, base_url: str, api_key: str, api_version: str = "v3", timeout: int = 30):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.api_path = f"/api/{api_version}"
        self._client: httpx.AsyncClient | None = None

    async def connect() / async def disconnect()
    async def health() -> bool
    async def _request(method, path, params, json) -> dict
    async def _get_paginated(path, params) -> list  # auto-paginate
    async def get_entities(entity_type, **query)      # Generic CRUD on /{entity_type}
    async def get_entity(entity_type, id)
    async def create_entity(entity_type, data)
    async def update_entity(entity_type, id, data)
    async def delete_entity(entity_type, id)
    async def lookup(entity_type, term)               # Search via /{entity}/lookup?term=
    async def get_queue(**filters) -> list
    async def get_history(**filters) -> list
    async def get_calendar(start, end) -> list
    async def get_wanted_missing(**filters) -> list
    async def trigger_command(name, **kwargs) -> dict
    async def get_system_status() -> dict
    async def get_disk_space() -> list
```

Bazarr uses a **separate** service class (`BazarrService`) because it is NOT Servarr-derived. It wraps `httpx.AsyncClient` directly.

---

## Phase 4: Service Layer

Each service extends `ArrClient` and adds app-specific methods:

### 4.1 RadarrService
- `get_movies()`, `add_movie(tmdb_id, quality_profile_id, root_folder_path)`
- `search_new(tmdb_id)` — lookup + add workflow
- `delete_movie(id, delete_files=False)`
- `get_movie(id)`, `update_movie(id, data)`
- `lookup_movie(term)` — search TMDb
- Quality profiles, root folders, import lists
- Calendar, queue, history, blocklist
- API: `GET/POST/DELETE /api/v3/movie`, `GET /api/v3/movie/lookup`

### 4.2 SonarrService
- `get_series()`, `add_series(tvdb_id, quality_profile_id, root_folder_path)`
- `search_new(tvdb_id)` — lookup + add
- `delete_series(id, delete_files=False)`
- `get_series(id)`, `get_episodes(series_id)`
- `lookup_series(term)` — search TVDB
- `get_episode_files(series_id)`
- Release profiles, language profiles
- API: `GET/POST/DELETE /api/v3/series`, `GET /api/v3/series/lookup`, `GET /api/v3/episode`

### 4.3 LidarrService
- `get_artists()`, `add_artist(foreign_artist_id, quality_profile_id, root_folder_path)`
- `search_new(foreign_artist_id)` — MusicBrainz ID
- `delete_artist(id, delete_files=False)`
- `get_artist(id)`, `get_albums(artist_id)`
- `lookup_artist(term)` — search MusicBrainz
- Metadata profiles
- API: `GET/POST/DELETE /api/v1/artist`, `GET /api/v1/artist/lookup`, `GET /api/v1/album`

### 4.4 ReadarrService
- `get_authors()`, `add_author(foreign_author_id, quality_profile_id, root_folder_path)`
- `search_new(foreign_author_id)` — Goodreads ID
- `delete_author(id, delete_files=False)`
- `get_author(id)`, `get_books(author_id)`
- `lookup_author(term)`, `lookup_book(term)`
- Editions, metadata profiles
- API: `GET/POST/DELETE /api/v1/author`, `GET /api/v1/author/lookup`, `GET /api/v1/book`

### 4.5 ProwlarrService
- `get_indexers()`, `add_indexer(config, name)`, `delete_indexer(id)`
- `test_indexer(id)`, `test_all_indexers()`
- `search_indexers(query, type="search")` — unified search across all indexers
- `get_applications()` — sync children (Radarr, Sonarr, Lidarr)
- `add_application(app_type, sync_level, base_url, api_key)` — register a child *arr
- `get_app_profiles()`, `get_tags()`, `get_notifications()`
- `get_stats()` — grabs, failures, queries by indexer
- `trigger_sync(application_id)` — force full sync to child
- API: `GET/POST/DELETE /api/v1/indexer`, `GET /api/v1/search`, `GET/POST /api/v1/applications`

### 4.6 BazarrService (standalone, NOT ArrClient)
- `get_system_status()` — version, start time, stats
- `get_movies()`, `get_episodes()`, `get_series()`
- `search_subtitles(movie_id / episode_id, language)` — manual search
- `download_subtitles(media_id, subtitle_info)` — trigger download
- `get_subtitle_history(limit)`
- `get_providers()` — list enabled subtitle providers
- `get_languages()` — language profiles
- `upload_subtitles(media_id, subtitle_file)` — custom subtitle upload
- `blacklist_subtitles(subtitle_id)` — avoid re-download
- API: `GET/POST /api/system/status`, `/api/movies`, `/api/episodes`, `/api/subtitles`, `/api/providers`, `/api/languages`

### 4.7 JellyfinBridge (cross-arr orchestration HTTP client)
- `check_availability(query: str, media_type: str)` — search Jellyfin library via HTTP
- Returns `{"available": bool, "item": {...}}` or `{"available": False}`
- No dependency on jellyfin-mcp — standalone httpx GET to Jellyfin REST API

---

## Phase 5: Tool Layer (Portmanteau Pattern)

### 5.1 Tool Registration Pattern

Follows the **jellyfin-mcp** dual pattern exactly:

1. **Portmanteau** (`tools/portmanteau/__init__.py`): Each tool decorated with `@mcp.tool()` from `...app import mcp`. Registered at import time via `from .tools import portmanteau` in `server.py`.

2. **Agentic** (`tools/agentic.py`): `register_agentic_arr_tools(mcp)` called explicitly in `server.py`.

3. **Conditional registration**: Each tool checks `config.*_enabled` before executing. If a service is disabled, the tool returns a clear "service not configured" message.

4. **All tools use**: `version="1.0.0"`, `annotations={"readOnlyHint": True/False, "destructiveHint": True/False}`, return `ToolResult`.

### 5.2 Portmanteau Tool Specification

| Tool | Operations | Read-Only? | Destructive? |
|------|-----------|------------|-------------|
| `arr_radarr` | list, add, lookup, search, delete, get, update, refresh, queue, history, calendar, wanted, quality_profiles, root_folders, import_lists, tags, blocklist, diskspace, status | No | Yes (add/delete/update/refresh) |
| `arr_sonarr` | list, add, lookup, search, delete, get, update, episodes, refresh, queue, history, calendar, wanted, quality_profiles, root_folders, tags, diskspace, status, language_profiles | No | Yes |
| `arr_lidarr` | list, add, lookup, search, delete, get, update, albums, refresh, queue, history, calendar, wanted, quality_profiles, root_folders, tags, diskspace, status, metadata_profiles | No | Yes |
| `arr_readarr` | list, add, lookup, search, delete, get, update, books, refresh, queue, history, calendar, wanted, quality_profiles, root_folders, tags, diskspace, status, metadata_profiles | No | Yes |
| `arr_prowlarr` | list_indexers, add_indexer, delete_indexer, test_indexer, test_all, search, stats, list_apps, add_app, delete_app, sync_app, status, history | No | Yes (add/delete/sync) |
| `arr_bazarr` | status, list_movies, list_episodes, search_subtitles, download, history, providers, languages, upload, blacklist, scan_disk | No | No (read-only except download/scan) |
| `arr_health` | check_all, check_radarr, check_sonarr, check_lidarr, check_readarr, check_prowlarr, check_bazarr, check_jellyfin | Yes | No |
| `arr_orchestrate` | queue_media (title + type → check Jellyfin → if missing, queue in appropriate *arr), check_all_sources, bulk_import | No | Yes |
| `arr_help` | discover | Yes | No |

### 5.3 Operation Enum Design

Each portmanteau tool uses `operation: Annotated[Literal[...], Field(description="...")]` with `Literal` types (NOT plain `str`). Example:

```python
@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": True})
async def arr_radarr(
    operation: Annotated[
        Literal["list", "add", "lookup", "search", "delete", "get", "update",
                "refresh", "queue", "history", "calendar", "wanted",
                "quality_profiles", "root_folders", "import_lists",
                "tags", "blocklist", "diskspace", "status"],
        Field(description="Radarr operation to perform."),
    ],
    ...
) -> ToolResult:
    """Manage Radarr movie library: add, search, delete, monitor queue, history, and configuration.
    ...
    """
```

### 5.4 Cross-Arr Orchestrator (`arr_orchestrate`)

**This is the differentiating feature.** Given a media title and type:

1. Check Jellyfin availability via HTTP (optional, if configured)
   - `GET http://jellyfin:8096/Items?searchTerm={title}&IncludeItemTypes={Movie,Series,MusicAlbum,Audio}`
   - If found → return `{"already_available": True, "source": "jellyfin", "item": {...}}`
2. If not in Jellyfin, determine target *arr:
   - `movie` → Radarr
   - `show` → Sonarr
   - `music` / `artist` → Lidarr
   - `book` / `author` → Readarr
3. Search target *arr for existing entry (avoid duplicates)
4. If not found, queue it:
   - Look up external ID (use lookup endpoint on target *arr)
   - Add with default quality profile and root folder (configurable)

Operations:
- `queue_media`: Single title → availability check → queue workflow
- `check_all_sources`: Check Jellyfin + all configured *arrs for a title
- `bulk_import`: Process a list of titles (array of `{title, type}` objects)

---

## Phase 6: FastMCP App Layer (`app.py`)

Follows jellyfin-mcp pattern exactly:

```python
mcp = FastMCP(
    "ArrMCP",
    instructions = "...",         # Summary of all tools
    lifespan = _arr_lifespan,     # Health-check all configured services
    sampling_handler = None,      # (Phase 7 optional)
    on_duplicate = "replace",
    strict_input_validation = True,
)
```

### 6.1 Lifespan Hook

During `_arr_lifespan`:
- Load `ArrConfig` from env
- For each enabled service, instantiate the service, call `health()`
- Store connected services in `app.state`
- On shutdown, close all httpx clients

### 6.2 Resources

- `resource://arr/quickstart` — getting started guide
- `resource://arr/services` — configured services matrix

### 6.3 Prompts

- `arr_setup_guide` prompt — helps agents configure arr-mcp

---

## Phase 7: Agentic Tools (`tools/agentic.py`)

### 7.1 `register_agentic_arr_tools(mcp)`

Programmatically registers the cross-arr orchestration tool with sampling support:

- `arr_agentic_orchestrate`: LLM-powered version that can use the sampling API to make decisions about:
  - Which *arr to use when type is ambiguous
  - Smart quality/profile selection based on media type
  - Tag generation for organization
  - Conflict resolution (multiple matches)

---

## Phase 8: Webapp Dashboard (Phase 8, Post-MCP)

React dashboard on port 10857:
- "*Arr Stack Status" overview: health indicators per service, queue counts, disk space, grab stats
- Quick-add: search any *arr via typeahead
- Prowlarr indexer status and stats
- Cross-arr queue viewer (pending downloads from all services)
- Jellyfin availability panel

Matches jellyfin-mcp webapp pattern (Vite/React, prefab-ui cards, Biome lint).

---

## Supporting Files

### `.env.example`

```env
# Transport
ARR_MCP_TRANSPORT=stdio
ARR_MCP_PORT=10856
ARR_MCP_HOST=127.0.0.1

# Radarr (http://localhost:7878)
RADARR_URL=http://localhost:7878
RADARR_API_KEY=
RADARR_ENABLED=false

# Sonarr (http://localhost:8989)
SONARR_URL=http://localhost:8989
SONARR_API_KEY=
SONARR_ENABLED=false

# Lidarr (http://localhost:8686)
LIDARR_URL=http://localhost:8686
LIDARR_API_KEY=
LIDARR_ENABLED=false

# Readarr (http://localhost:8787)
READARR_URL=http://localhost:8787
READARR_API_KEY=
READARR_ENABLED=false

# Prowlarr (http://localhost:9696)
PROWLARR_URL=http://localhost:9696
PROWLARR_API_KEY=
PROWLARR_ENABLED=false

# Bazarr (http://localhost:6767)
BAZARR_URL=http://localhost:6767
BAZARR_API_KEY=
BAZARR_ENABLED=false

# Jellyfin bridge (cross-arr orchestration)
JELLYFIN_URL=http://localhost:8096
JELLYFIN_API_KEY=
JELLYFIN_ENABLED=false

# Shared
ARR_TIMEOUT=30
```

### `pyproject.toml` key excerpts

```toml
[project]
name = "schip-mcp-arr"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastmcp>=3.2.0",
    "httpx>=0.25.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "python-dotenv>=1.0.0",
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
]

[project.scripts]
arr-mcp = "arr_mcp.server:main"
```

### `justfile` recipes

Standard fleet justfile: `install`, `start`, `webapp`, `lint`, `fix`, `fmt`, `test`, `ci`, `clean`.

---

## Implementation Order (8 Phases)

| Phase | What | Files | Tests |
|-------|------|-------|-------|
| **1** | Scaffold: pyproject.toml, justfile, .env.example, .gitignore, dirs, CI | 7 files | — |
| **2** | Config layer: ArrConfig model, env loading, validation | `config.py` | `test_config.py` |
| **3** | Base client: ArrClient + tests | `services/base.py`, `services/arr_client.py` | `test_arr_client.py` |
| **4** | Service layer: all 7 services | `services/{radarr,sonarr,lidarr,readarr,prowlarr,bazarr,jellyfin}.py` | per-service tests |
| **5** | Tool layer: all 9 portmanteau tools + agentic | `tools/portmanteau/*.py`, `tools/agentic.py` | per-tool tests |
| **6** | App layer: FastMCP instance, lifespan, resources, prompts, server.py, transport.py | `app.py`, `server.py`, `transport.py` | integration tests |
| **7** | Agentic tools: sampling-based orchestration | `tools/agentic.py` (enhanced) | `test_agentic.py` |
| **8** | Webapp dashboard (React frontend) | `webapp/` | e2e tests |

---

## API Surface Summary

### Radarr API (v3, port 7878)
```
GET    /api/v3/health
GET    /api/v3/system/status
GET    /api/v3/movie                    # list all
GET    /api/v3/movie/{id}               # get one
POST   /api/v3/movie                    # add (requires tmdbId, qualityProfileId, rootFolderPath)
PUT    /api/v3/movie/{id}               # update
DELETE /api/v3/movie/{id}               # delete
GET    /api/v3/movie/lookup?term=       # search TMDb
GET    /api/v3/queue
GET    /api/v3/history
GET    /api/v3/calendar?start=&end=
GET    /api/v3/wanted/missing
POST   /api/v3/command                  # RefreshMovie, RescanMovie, RssSync
GET    /api/v3/qualityprofile
GET    /api/v3/rootfolder
GET    /api/v3/importlist
GET    /api/v3/tag
GET    /api/v3/blocklist
GET    /api/v3/diskspace
GET    /api/v3/notification
```

### Sonarr API (v3, port 8989)
```
GET    /api/v3/health
GET    /api/v3/system/status
GET    /api/v3/series                  # list all
GET    /api/v3/series/{id}             # get one
POST   /api/v3/series                  # add (requires tvdbId, qualityProfileId, rootFolderPath)
PUT    /api/v3/series/{id}             # update
DELETE /api/v3/series/{id}             # delete
GET    /api/v3/series/lookup?term=     # search TVDB
GET    /api/v3/episode?seriesId=       # list episodes
GET    /api/v3/episode/{id}            # get episode
PUT    /api/v3/episode/{id}            # update episode (monitor toggle)
GET    /api/v3/episodefile?seriesId=   # episode files
GET    /api/v3/queue
GET    /api/v3/history
GET    /api/v3/calendar?start=&end=
GET    /api/v3/wanted/missing
POST   /api/v3/command                  # RefreshSeries, RescanSeries, RssSync, EpisodeSearch
GET    /api/v3/qualityprofile
GET    /api/v3/languageprofile          # Sonarr v3 only (v4 uses custom formats)
GET    /api/v3/rootfolder
GET    /api/v3/tag
GET    /api/v3/releaseprofile
GET    /api/v3/diskspace
GET    /api/v3/notification
```

### Lidarr API (v1, port 8686)
```
GET    /api/v1/health
GET    /api/v1/system/status
GET    /api/v1/artist                  # list all
GET    /api/v1/artist/{id}             # get one
POST   /api/v1/artist                  # add
PUT    /api/v1/artist/{id}             # update
DELETE /api/v1/artist/{id}             # delete
GET    /api/v1/artist/lookup?term=     # search MusicBrainz
GET    /api/v1/album?artistId=
GET    /api/v1/queue
GET    /api/v1/history
GET    /api/v1/calendar?start=&end=
GET    /api/v1/wanted/missing
POST   /api/v1/command                  # RefreshArtist, RssSync, AlbumSearch
GET    /api/v1/qualityprofile
GET    /api/v1/metadataprofile
GET    /api/v1/rootfolder
GET    /api/v1/tag
GET    /api/v1/diskspace
```

### Readarr API (v1, port 8787)
```
GET    /api/v1/health
GET    /api/v1/system/status
GET    /api/v1/author                  # list all
GET    /api/v1/author/{id}             # get one
POST   /api/v1/author                  # add
PUT    /api/v1/author/{id}             # update
DELETE /api/v1/author/{id}             # delete
GET    /api/v1/author/lookup?term=     # search
GET    /api/v1/book?authorId=
GET    /api/v1/book/lookup?term=
GET    /api/v1/queue
GET    /api/v1/history
GET    /api/v1/wanted/missing
POST   /api/v1/command                  # RefreshAuthor, RssSync, BookSearch
GET    /api/v1/qualityprofile
GET    /api/v1/metadataprofile
GET    /api/v1/rootfolder
GET    /api/v1/tag
GET    /api/v1/diskspace
```

### Prowlarr API (v1, port 9696)
```
GET    /api/v1/health
GET    /api/v1/system/status
GET    /api/v1/indexer                 # list all
POST   /api/v1/indexer                 # add
PUT    /api/v1/indexer/{id}            # update
DELETE /api/v1/indexer/{id}            # delete
POST   /api/v1/indexer/test            # test single
POST   /api/v1/indexer/testall         # test all
GET    /api/v1/search?query=&type=&indexerIds=
GET    /api/v1/appprofile
GET    /api/v1/applications            # list synced *arr apps
POST   /api/v1/applications            # add child app
DELETE /api/v1/applications/{id}       # remove
GET    /api/v1/history
GET    /api/v1/stats
GET    /api/v1/tag
GET    /api/v1/notification
GET    /api/v1/diskspace
```

### Bazarr API (v1, port 6767)
```
GET    /api/system/status
GET    /api/movies
GET    /api/movies/{id}
GET    /api/episodes?seriesId=
GET    /api/episodes/{id}
GET    /api/series
GET    /api/series/{id}
GET    /api/subtitles?movieId=|episodeId=&language=
POST   /api/subtitles                 # download subtitle
GET    /api/subtitles/history
DELETE /api/subtitles/history/{id}
GET    /api/providers
GET    /api/languages
GET    /api/languages/profile
POST   /api/notifications/test
POST   /api/system/tasks              # trigger scan disk
```

### Jellyfin API (availability check only, port 8096)
```
GET /Items?searchTerm={title}&IncludeItemTypes={Movie,Series,MusicAlbum,Audio,book}&Recursive=true
Headers: X-MediaBrowser-Token: {api_key}
```

---

## Error Handling Strategy

Per the fleet base.py pattern:
- `ServiceError(code, message, details)` — base
- `AuthenticationError` — bad API key (401)
- `ConnectionError` — unreachable (timeout, connection refused)
- `NotFoundError` — resource not found (404)

All tools wrap in try/except and return `ToolResult(content={"success": False, "error": str(e)})`.

---

## Testing Strategy

- **Unit**: Each service method mocked with `pytest-httpx` / `respx`
- **Integration**: Full server boot with mock services, test tool calls end-to-end
- **E2E**: (Phase 8) Playwright tests against React dashboard

---

**This plan is ready for review. No code has been written yet.** Confirm the architecture, ports (10856/10857), and feature scope before Phase 1 scaffolding begins.
