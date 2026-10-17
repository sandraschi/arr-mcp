# arr-mcp — MCP Server Capabilities

## Server Overview

arr-mcp is a unified FastMCP 3.3+ server for the complete *arr automation stack. It provides a single MCP interface to Radarr (movies), Sonarr (TV series), Lidarr (music), Prowlarr (indexers), Readarr (books), Overseerr (media requests), and Bazarr (subtitles). Each service is independently optional — if a service is not configured, its tools are simply not registered.

**The differentiator:** The `arr_orchestrate` tool chains media server availability checks (Jellyfin + Plex + Emby) with automatic *arr routing. Given a media title, it checks configured media servers, and if not found, auto-routes to the correct *arr service for acquisition.

**Stack architecture:** arr-mcp auto-discovers services on default ports when an API key is found in the environment. Service tools are conditionally registered — each service client is independently initialized, and missing services gracefully skip tool registration. The server also provides Prefab UI cards for health status, calendar, and stack statistics.

## Tools

### Radarr: radarr_movies

Portmanteau tool for movie management across the full lifecycle.

**Operations:** `list`, `lookup`, `get`, `add`, `delete`, `update`, `import`

**Parameters (by operation):**
- `list`: No additional parameters needed.
- `lookup`: Requires `term` (str) — search term for movie lookup.
- `get`: Requires `movie_id` (int) — Radarr movie ID.
- `add`: Requires `tmdb_id` (int), `quality_profile_id` (int), `root_folder_path` (str). Optional: `title` (str), `monitored` (bool, default True), `search_for_movie` (bool, default True).
- `delete`: Requires `movie_id` (int). Optional: `delete_files` (bool, default False).
- `update`: Requires `movie_id` (int). Optional: `monitored` (bool).
- `import`: Requires `folder` (str) — path for manual import.

**Return format:** `{"success": bool, "message": str, "data": list|dict}`

### Sonarr: sonarr_series / sonarr_episodes

Two portmanteau tools for TV series and episode management.

**sonarr_series operations:** `list`, `lookup`, `get`, `add`, `delete`, `update`
- `lookup`: Requires `term` (str).
- `add`: Requires `tvdb_id` (int), `quality_profile_id` (int), `root_folder_path` (str). Optional: `title`, `monitored` (default True), `search_for_missing` (default True).
- `delete`: Requires `series_id` (int). Optional: `delete_files` (default False).

**sonarr_episodes operations:** `list`, `get`, `search`, `set_monitored`
- `list`: Requires `series_id` (int). Optional: `season_number` (int) to filter.
- `get`: Requires `episode_id` (int).
- `search`: Requires `episode_id` (int) or `series_id` (int).
- `set_monitored`: Requires `episode_id` (int), `monitored` (bool).

### Lidarr: lidarr_artists / lidarr_albums

Two portmanteau tools for music artist and album management.

**lidarr_artists operations:** `list`, `lookup`, `get`, `add`, `delete`, `update`
- `add`: Requires `foreign_artist_id` (str, MusicBrainz ID), `quality_profile_id` (int), `root_folder_path` (str).

**lidarr_albums operations:** `list`, `get`, `lookup`, `set_monitored`
- `list`: Requires `artist_id` (int).
- `lookup`: Requires `term` (str).

### Readarr: readarr_authors / readarr_books

Two portmanteau tools for author and book management.

**readarr_authors operations:** `list`, `lookup`, `get`, `add`, `delete`, `update`
- `add`: Requires `foreign_author_id` (str), `quality_profile_id` (int), `root_folder_path` (str).

**readarr_books operations:** `list`, `get`, `lookup`, `set_monitored`
- `list`: Requires `author_id` (int).
- `lookup`: Requires `term` (str).

### Prowlarr: prowlarr_indexers / prowlarr_search / prowlarr_applications / prowlarr_history

Four portmanteau tools for indexer backbone management.

**prowlarr_indexers operations:** `list`, `get`, `add`, `update`, `delete`, `test`, `test_all`, `schema`
- `add`: Requires `name` (str), `config_contract` (str, e.g. "NewznabSettings"). Optional: `enable_rss` (default True), `enable_search` (default True), `priority` (default 25).

**prowlarr_search operation:** `search` — unified search across all indexers. Requires `query` (str). Optional: `type` (movie/search/book/tvsearch), `indexer_ids` (list[int]), `limit` (int, default 30).

**prowlarr_applications operations:** `list`, `get`, `sync`, `sync_all`, `test`
- `sync`: Requires `app_id` (int). `sync_all`: No additional params.

**prowlarr_history operations:** `list`, `since`, `by_indexer`
- `since`: Requires `date` (ISO datetime).

### Overseerr: overseerr_requests / overseerr_search / overseerr_users

Three portmanteau tools for media request management.

**overseerr_requests operations:** `list`, `get`, `create`, `approve`, `decline`, `delete`, `count`, `pending`
- `create`: Requires `media_type` ("movie"/"tv"), `media_id` (int). Optional: `seasons` (list[int] for TV), `is4k` (bool).
- `approve`/`decline`/`get`/`delete`: Require `request_id` (int).

**overseerr_search operation:** `search` — search for media to request. Requires `query` (str).

**overseerr_users operations:** `list`, `get`, `create`, `update`, `delete`
- `get`: Requires `user_id` (int).

### Bazarr: bazarr_subtitles

Portmanteau tool for subtitle management across the stack.

**Operations:** `wanted`, `search`, `download`, `history`, `providers`, `languages`
- `search`: Requires `episode_id` (int) or `movie_id` (int). Optional: `language` (str, e.g. "en", "de").
- `download`: Requires `subtitle_path` (str), `episode_id` or `movie_id`. Optional: `language`, `provider` (str), `scene_name` (str).

### Cross-Arr Orchestration: arr_orchestrate

**THE DIFFERENTIATOR** — chains media server checks with auto-routing.

**Operations:** `request`, `status`, `check_jellyfin`, `check_plex`, `check_emby`, `queue`
- `request`: Requires `media_title` (str). Optional: `media_type` (movie/series/album/book — auto-detected), `year` (int), `quality_profile_id`, `root_folder_path`.
- `check_jellyfin`/`check_plex`/`check_emby`: Requires `media_title` (str).
- `status`: Returns full stack status.
- `queue`: Returns active download queues.

### Stack Health: arr_health

**Parameters:**
- `service` (Literal, default "all"): `all`, `radarr`, `sonarr`, `lidarr`, `prowlarr`, `readarr`, `overseerr`, `bazarr`.

**Return format:** `{"success": bool, "message": "X/Y services reachable", "data": {service_name: {"reachable": bool, "version": str, "reason": str}}}`

### Unified Calendar: arr_calendar

Aggregates upcoming releases from Radarr, Sonarr, Lidarr, and Readarr.

**Operations:** `upcoming`, `today`, `week`, `range`
- `range`: Requires `start` (ISO datetime), `end` (ISO datetime). Optional: `types` (list of media types to filter).

### Stack Statistics: arr_stats

**Operations:** `summary`, `disk`, `queues`, `history`

### Agentic Workflows: arr_agentic

Uses FastMCP sampling (SEP-1577) for LLM-powered cross-arr operations. The LLM decides which tools to call and in what order.

**Operations:** `workflow`, `natural_query`
- `workflow`: Multi-step task described in natural language. Examples: "add The Matrix to Radarr with best quality."
- `natural_query`: Ask a question about your media stack. Examples: "what's the most wanted movie right now?"

### Help: arr_help

**Operations:** `discover`, `tool_info`, `quickstart`
- `discover`: Lists all available tools.
- `tool_info`: Requires `tool_name` (str).
- `quickstart`: Step-by-step guide.

### Prefab UI Cards: arr_health_card / arr_calendar_card / arr_stats_card

Rich visual cards rendered in supporting MCP clients.
- `arr_health_card()`: Stack health as a live card.
- `arr_calendar_card(days=14)`: Upcoming releases card.
- `arr_stats_card()`: Consolidated statistics card.

### Health & Diagnostics: api_health / api_logs / api_logs_stream

- `api_health`: Server health check endpoint.
- `api_logs`: Recent server logs (up to 500 entries from ring buffer).
- `api_logs_stream`: SSE endpoint for real-time log streaming.

## Configuration

Each *arr service is configured independently via environment variables. Service discovery uses the following defaults:

| Variable | Default Port | Purpose |
|----------|-------------|---------|
| `RADARR_URL` / `RADARR_API_KEY` | 7878 | Radarr movie management |
| `SONARR_URL` / `SONARR_API_KEY` | 8989 | Sonarr TV series management |
| `LIDARR_URL` / `LIDARR_API_KEY` | 8686 | Lidarr music management |
| `PROWLARR_URL` / `PROWLARR_API_KEY` | 9696 | Prowlarr indexer backbone |
| `READARR_URL` / `READARR_API_KEY` | 8787 | Readarr book management |
| `OVERSEERR_URL` / `OVERSEERR_API_KEY` | 5055 | Overseerr media requests |
| `BAZARR_URL` / `BAZARR_API_KEY` | 6767 | Bazarr subtitle management |
| `JELLYFIN_URL` / `JELLYFIN_API_KEY` | 8096 | Jellyfin media server bridge |
| `PLEX_URL` / `PLEX_TOKEN` | 32400 | Plex media server bridge |
| `EMBY_URL` / `EMBY_API_KEY` | 8096 | Emby media server bridge |
| `ARR_LOG_LEVEL` | INFO | Logging verbosity |

### Ports

| Service | Port |
|---------|------|
| arr-mcp backend | 10938 |
| arr-mcp frontend | 10939 |

## Resources

| Resource | Description |
|----------|-------------|
| `arr://config` | Current server configuration summary |
| `arr://quickstart` | Quickstart guide for new users |
| `arr://help` | Tool documentation index |
| `arr://capabilities` | Available service capabilities |

## Prompts

| Prompt | Description |
|--------|-------------|
| `orchestrate_media` | Guide the LLM through media request orchestration |
| `stack_health_check` | Walkthrough for diagnosing stack health issues |

## Error Handling

All tools return structured dicts with `{"success": bool, "message": str, "data": ...}` pattern. Service-specific errors include descriptive messages. When a service is not configured, tools are simply not registered — no error is raised. Timeouts and network failures return structured error messages with the exception detail. The `arr_agentic` tool falls back gracefully when sampling is unavailable.

## Readarr Book Mutations: readarr_add_book / readarr_delete_book / readarr_delete_books / readarr_add_options

Readarr's API exposes books but no safe single-call add/delete path, so arr-mcp
ships four dedicated tools with exact-ID semantics and dry-run-first deletion.

**readarr_add_book** — add exactly one book using an exact lookup edition.
Either pass `author_id` (reuse that author's configuration) or the complete
new-author set (`foreign_author_id`, `quality_profile_id`, `metadata_profile_id`,
`root_folder_path`). New-author monitoring maps to Readarr's author add options:
`monitor` is one of specific_book, all, future, missing, existing, first, latest,
none (default specific_book); `monitor_new_books` is all, none, or new (default
none). `tags` accepts existing Readarr tag IDs only. The legacy aliases
`monitored` (bool) and `search_for_new_book` (bool) are retained for older callers;
new callers use `monitor`/`monitor_new_books`. Set `search_for_new_book=true` to
trigger Readarr's native download search immediately after adding. Duplicate
protection: if a book with the same `foreign_book_id` already exists, the tool
refuses with the existing record instead of creating a duplicate. A matching
release may download under the author's quality profile; adding never enables
searching the author's other books.

**readarr_delete_book** — preview (default `dry_run=true`) or delete one book;
the author is always retained. `delete_files=true` additionally requires
`confirm_delete_files=true`, otherwise the tool refuses even outside dry-run
mode. `add_import_list_exclusion=true` adds an import-list exclusion so the book
is not re-grabbed. Returns the preview (book record plus file list) in both
modes so callers can show what would happen before committing.

**readarr_delete_books** — bulk variant for up to 100 unique IDs per call
(duplicates removed). Every ID is preflighted before the first mutation; any
preflight failure aborts the whole batch with zero deletions. A mid-sequence
delete failure stops the run and reports `deleted`, `failed`, and
`not_attempted` so the caller knows exactly where it stopped. Same
`dry_run`/`delete_files`/`confirm_delete_files`/`add_import_list_exclusion`
contract as the single variant. Authors are never deleted by either tool.

**readarr_add_options** — read-only discovery of the choices `readarr_add_book`
needs for a new author: root folders (id, name, path, freeSpace, default
quality/metadata profile IDs, default tags — Calibre connection settings are
stripped, only UI choices are returned), quality profiles, metadata profiles,
existing tags, plus the legal `monitor_modes` and `monitor_new_books_modes`
lists. Call this before any new-author add instead of guessing IDs.

## Sonarr Episodes: sonarr_episodes

**Operations:** `list`, `get`, `search`, `set_monitored`. `list` requires
`series_id` with optional `season_number` filter. `get` requires `episode_id`.
`search` requires `episode_id` or `series_id` and triggers Sonarr's native
search for missing episodes. `set_monitored` requires `episode_id` plus
`monitored` bool. Episode monitoring composes with series monitoring: an
unmonitored series ignores episode-level flags, so check the series record
first when a monitored episode never grabs.

## Lidarr Albums: lidarr_albums

**Operations:** `list`, `get`, `lookup`, `set_monitored`. `list` requires
`artist_id`. `lookup` takes a `term` string against MusicBrainz. New artists are
added via `lidarr_artists` with a MusicBrainz `foreign_artist_id`; albums
inherit the artist's quality profile and root folder. `set_monitored` toggles
per-album monitoring for back-catalog control.

## Prowlarr Detail: applications, history, indexer ops

**prowlarr_applications operations:** `list`, `get`, `sync`, `sync_all`, `test`.
`sync` pushes the indexer list to one connected *arr app by `app_id`;
`sync_all` fans out to every connected app after indexer changes — call it after
any `prowlarr_indexers` add/update/delete or the apps keep stale indexer lists.

**prowlarr_history operations:** `list`, `since`, `by_indexer`. `since` takes an
ISO datetime and returns grabs/failures after that point; `by_indexer` groups
activity per indexer for spotting dead or failing indexers. Pair with
`prowlarr_indexers(operation="test_all")` for a full indexer health pass.

**prowlarr_indexers full ops:** `list`, `get`, `add`, `update`, `delete`,
`test`, `test_all`, `schema`. `schema` returns the config-contract fields for
an indexer implementation (needed before `add` with a new `config_contract`
such as NewznabSettings). `test` validates one indexer by ID without changing
anything.

## Overseerr Detail: search and users

**overseerr_search operation:** `search` — free-text search across Overseerr's
movie/TV catalog. Requires `query`. Use it to resolve the exact `media_id`
before `overseerr_requests(operation="create")`; creating with a guessed ID is
the most common request failure.

**overseerr_users operations:** `list`, `get`, `create`, `update`, `delete`.
`get` requires `user_id`. Request approval workflows key off Overseerr users,
so resolve the requester's user record when triaging who asked for what.

## Bazarr Detail: providers, languages, history

**Operations:** `wanted`, `search`, `download`, `history`, `providers`,
`languages`. `providers` lists configured subtitle providers and their status —
check it first when searches come back empty. `languages` lists enabled subtitle
languages. `history` shows past subtitle downloads. `wanted` lists episodes and
movies missing subtitles in enabled languages. Subtitle files retrieved through
Bazarr can feed downstream analysis pipelines (notably jellyfin-mcp RAG).

## Orchestration Pipeline Stages

`arr_orchestrate(operation="request")` runs a fixed pipeline and returns each
step: (1) media-server availability — Jellyfin, then Plex, then Emby when
configured; already in library means done, no *arr call. (2) Media-type
detection — movie, series, album, or book, overridable via `media_type`.
(3) Queue check — already queued titles report position instead of
double-adding. (4) Add to the routed *arr with quality profile and root folder.
(5) Result with the created record ID. Placeholder credentials
(`your-*-api-key-here` from `.env.example`) count as unconfigured: media-server
checks skip them instead of erroring, and unreachable media servers yield
`<name>_error` pipeline steps rather than aborting the request.

## Media-Server Bridges

Three bridges back the availability checks with identical
`{"success", "message", "data"}` shapes: Jellyfin (`JELLYFIN_URL` +
`JELLYFIN_API_KEY`), Plex (`PLEX_URL` + `PLEX_TOKEN`), Emby (`EMBY_URL` +
`EMBY_API_KEY`). All optional; orchestration works without them and simply
skips the in-library check. `arr_orchestrate` operations `check_jellyfin`,
`check_plex`, `check_emby` probe one bridge each for a title.

## REST API Reference (webapp, `:10938/api/*`)

`health` (all-service probe), `capabilities` (server/services/features matrix),
`skills` (domain skill text for chat preprompts), `diagnostics` plus the
`/v1/diagnostics` alias (CUA-NSIS smoke: backend port/status, CPU/memory/disk,
tool total), `logs` (ring-buffer tail, `limit` param) and `logs/stream` (SSE
live tail), per-service `*/summary` endpoints (counts, wanted, queue, disk),
`orchestrator/summary`, `llm/discover` (Ollama/LM Studio presence),
`llm/providers` (registry with detected/configured flags, never key bytes),
`llm/models` (live model list per provider, `provider` + `base_url` params),
`llm/onboarding` (starter facts + recommended path), `llm/chat` (POST backend
proxy: provider, model, messages), `chat` (POST skill-first chat: message,
history capped at 20 turns, personality, provider, model — personalities are
arr-expert, media-curator, quick-summarizer, custom), `shutdown` (POST orderly
exit: responds 200 then exits so flows checkpoint). The webapp Chat page uses
only these endpoints — keys never leave the server, and the browser never
fetches Ollama/LM Studio directly.

## Delete-Safety Rules

Every destructive tool defaults to the safe mode: `dry_run=true` previews
without mutating; `delete_files` defaults false and additionally requires an
explicit confirmation flag. Servarr DELETE endpoints return HTTP 200 with an
empty body, which the client treats as success-with-empty-data rather than a
JSON decode failure — a regression test pins this behavior so future client
changes cannot reintroduce false failures. Authors, artists, and series are
never cascade-deleted by book/album/episode tools. Bulk deletes preflight
everything before mutating anything.

## Webapp Pages

Dashboard (live health cards per service, 15 s poll, hero with backend/LLM
status), per-service pages (Radarr, Sonarr, Lidarr, Prowlarr, Readarr,
Overseerr, Bazarr with counts/wanted/queue/disk), Orchestrate (pipeline viz +
stack overview), Chat (Ollama/LM Studio via backend proxy, skill-first
preprompt, personalities, persisted history), Inspector (interactive tool
runner: pick tool, set params, execute via `/mcp`, raw JSON-RPC response),
Inbox (ops feed), Tools (tool catalog with search/filter), Skills (skill
registry), Logger (SSE live logs with filter/export), Help (setup, Docker,
per-service install, API keys), Settings (LLM providers, backend health, port
reference). Health dot uses exponential-backoff polling against `/api/health`.

## Full Environment Reference

Service triples `*_URL`, `*_API_KEY`, `*_ENABLED` for RADARR, SONARR, LIDARR,
PROWLARR, READARR, OVERSEERR, BAZARR; `JELLYFIN_URL`/`JELLYFIN_API_KEY`,
`PLEX_URL`/`PLEX_TOKEN`, `EMBY_URL`/`EMBY_API_KEY`; `ARR_MCP_TRANSPORT`
(stdio|http|sse), `ARR_MCP_HOST`, `ARR_MCP_PORT` (default 10938),
`ARR_MCP_PATH` (default /mcp); `ARR_SAMPLING_BASE_URL`,
`ARR_SAMPLING_MODEL`, `ARR_SAMPLING_API_KEY` (agentic fallback LLM);
`ARR_LOG_LEVEL`, `ARR_TIMEOUT`. Auto-discovery: set an API key without a URL
and the server probes the service's default port. Backend `:10938`
(FastMCP HTTP `/mcp` + REST `/api/*` + SSE `/api/logs/stream`), frontend
`:10939` (Vite).

## Transport Modes

Stdio is the Claude Desktop path: the MCPB bundle runs `python -m arr_mcp`
with `MCP_TRANSPORT=stdio` and speaks JSON-RPC over standard IO. HTTP serves
the webapp, the Tauri sidecar, and container hosts: FastMCP's ASGI app mounts
at `/mcp` on a FastAPI parent that also carries `/api/*`, with stateless HTTP
and log level set via `FASTMCP_STATELESS_HTTP`/`FASTMCP_LOG_LEVEL` environment
variables (constructor kwargs were removed in FastMCP 3.3). Tauri spawns set
`ARR_TAURI=1`, which forces HTTP so the frozen backend opens the port the
webview polls. `POST /api/shutdown` responds 200 immediately and exits 500 ms
later so fleet launchers can bounce the process without losing in-flight work.
SSE transport is accepted alongside HTTP for streaming clients.

## Service Discovery Protocol

Each service client initializes independently at startup from its triple. URL
set plus key plus enabled means configured. Key set without URL means probe
the default port (Radarr 7878, Sonarr 8989, Lidarr 8686, Prowlarr 9696,
Readarr 8787, Overseerr 5055, Bazarr 6767, Jellyfin/Emby 8096, Plex 32400);
a responding port self-completes the URL. Unconfigured services skip tool
registration entirely, so the tool surface always reflects reality — a missing
`radarr_movies` means Radarr is not configured, never a bug. `arr_health`
reports per-service reachable/version/reason and is the first call in every
session. Media-server bridges follow the same pattern with placeholder-key
detection: example credentials never produce authenticated calls.

## Sampling Contract (arr_agentic)

`arr_agentic(operation, prompt, ctx)` prefers FastMCP 3.4 sampling: the stack
context (available services plus the user prompt) is sent as string messages
with a system prompt identifying the orchestrator role, capped at 1024 tokens.
The `SamplingResult.text` becomes the response with `sampling_used=true`. Any
sampling failure (unsupported client, timeout, error) falls back to a
structured brief — service inventory plus which concrete tools to call next —
with `sampling_used=false`. The tool never raises for sampling reasons; only
unexpected internal errors return `success=false`. Client agents without
sampling support should treat the fallback brief as the plan and execute the
named tools themselves in order, starting with the availability checks.

## Security Model

The server holds API keys in process memory from `.env`, never writes them to
logs, and never returns key bytes through any tool or endpoint — provider
registries expose detected/configured flags only. Destructive actions are
gated twice (dry-run default plus confirmation flags for disk deletes).
`.env` is gitignored fleet-wide; only `.env.example` with placeholders ships.
CORS uses an explicit origin list (backend/frontend localhost, Goliath LAN
name, Tauri schemes) plus an unconditional regex covering Tailscale MagicDNS;
the webapp calls same-origin relatively except behind the Tauri gate, where an
absolute backend URL is required. No tool shells out, no tool reads arbitrary
paths, and bulk mutations preflight before touching anything.

## Testing and Quality Gates

289 pytest tests with pytest-httpx HTTP mocking (service clients fully mocked;
no live *arr needed), coverage threshold 50 percent enforced in
`pyproject.toml` — current coverage holds above 60 percent, with thin spots on
the Prefab card builders and the HTTP transport runner that e2e smoke covers
instead. Ruff check plus format-check, mypy over `src/arr_mcp`, Biome
check plus `tsc -b` plus production build for the webapp, Playwright e2e smoke
covering every page. CI runs backend and webapp jobs on windows-latest with
Node 22 and `astral-sh/setup-uv`. Launcher contract: `fleet-start.config.ps1`
declares module-serve `arr_mcp` with `--http --port 10938` and `/api/health`;
the fleet engine probes it before opening the frontend.
