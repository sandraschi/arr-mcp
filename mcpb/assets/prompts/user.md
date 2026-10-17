# arr-mcp — User Guide

## Quick Start

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/sandraschi/arr-mcp.git
   cd arr-mcp
   ```

2. **Install dependencies:**
   ```bash
   uv sync
   ```

3. **Configure `.env`:**
   ```env
   RADARR_API_KEY=your_radarr_api_key
   SONARR_API_KEY=your_sonarr_api_key
   # Optional services:
   # LIDARR_API_KEY=...
   # PROWLARR_API_KEY=...
   # READARR_API_KEY=...
   # OVERSEERR_API_KEY=...
   # BAZARR_API_KEY=...
   ```

4. **Run the server:**
   ```bash
   uv run run_server.py
   ```

5. **Add to Claude Desktop:**
   ```json
   {
     "arr-mcp": {
       "command": "uv",
       "args": ["run", "--directory", "C:\\path\\to\\arr-mcp", "run_server.py"],
       "env": {"RADARR_API_KEY": "..."}
     }
   }
   ```

6. **Verify:**
   Call `arr_health()` to see which services are reachable.

## Tutorials

### Tutorial 1: Stack-Wide Health Check

The first thing to do is verify which *arr services are reachable.

```python
health = arr_health(service="all")
print(health['message'])
for service_name, status in health['data'].items():
    print(f"{service_name}: {'UP' if status.get('reachable') else 'DOWN'} {status.get('version', '')}")
```

### Tutorial 2: List and Search Movies (Radarr)

Discover what movies Radarr is managing.

```python
# List all movies
movies = radarr_movies(operation="list")
print(f"Total movies: {len(movies['data'])}")
for m in movies['data'][:5]:
    print(f"  {m.get('title')} ({m.get('year')})")

# Lookup a movie to add
results = radarr_movies(operation="lookup", term="Dune")
for r in results['data']:
    print(f"{r.get('title')} ({r.get('year')}) — TMDB: {r.get('tmdbId')}")
```

### Tutorial 3: Add a Movie to Radarr

Search, find, and add a movie with the desired quality profile.

```python
# Step 1: Look up the movie
results = radarr_movies(operation="lookup", term="The Matrix")
tmdb_id = results['data'][0]['tmdbId']

# Step 2: Add it with quality profile
result = radarr_movies(
    operation="add",
    tmdb_id=tmdb_id,
    title="The Matrix",
    quality_profile_id=1,
    root_folder_path="/media/Movies",
    search_for_movie=True
)
print(result['message'])
```

### Tutorial 4: Browse Sonarr Series

View and search TV series managed by Sonarr.

```python
# List all series
series = sonarr_series(operation="list")
print(f"Total series: {len(series['data'])}")

# Look up a specific show
found = sonarr_series(operation="lookup", term="Breaking Bad")
for s in found['data']:
    print(f"{s.get('title')} — TVDB: {s.get('tvdbId')}")
```

### Tutorial 5: Cross-Arr Orchestration

The killer feature — check media servers and auto-route to the correct *arr.

```python
# Check if a movie exists on your media server, then request it
result = arr_orchestrate(
    operation="request",
    media_title="Dune",
    media_type="movie",
    quality_profile_id=1,
    root_folder_path="/media/Movies"
)

# Show the pipeline steps
for step in result.get('pipeline', []):
    print(f"[{step.get('step')}] {step.get('action')}: {step.get('result', '')}")
```

### Tutorial 6: Unified Calendar

See upcoming releases across all *arr services.

```python
# Next two weeks
calendar = arr_calendar(operation="upcoming")
for service, items in calendar.get('data', {}).items():
    for item in items[:3]:
        print(f"[{service}] {item.get('title')} — {item.get('releaseDate')}")

# Specific date range
calendar = arr_calendar(operation="range", start="2026-06-01T00:00:00Z", end="2026-06-30T23:59:59Z")

# Filter by type
calendar = arr_calendar(operation="upcoming", types=["movie", "series"])
```

### Tutorial 7: Stack Statistics

Get consolidated statistics across the entire stack.

```python
# Summary
stats = arr_stats(operation="summary")
for service, data in stats.get('data', {}).items():
    print(f"{service}: {data.get('total', '?')} items, {data.get('wanted', '?')} wanted")

# Disk usage
disk = arr_stats(operation="disk")
for mount, usage in disk.get('data', {}).items():
    print(f"{mount}: {usage.get('freeSpace') / 1e9:.1f} GB free")

# Active queues
queues = arr_stats(operation="queues")
print(f"Queued items: {queues.get('total', 0)}")
```

### Tutorial 8: Prowlarr Indexer Management

Manage your Usenet and Torrent indexers.

```python
# List all configured indexers
indexers = prowlarr_indexers(operation="list")
for idx in indexers['data']:
    print(f"{idx.get('name')} — {idx.get('configContract')} — {'enabled' if idx.get('enableRss') else 'disabled'}")

# Test a specific indexer
test = prowlarr_indexers(operation="test", indexer_id=1)
print(test['message'])

# Test all indexers at once
test_all = prowlarr_indexers(operation="test_all")
```

### Tutorial 9: Manage Media Requests (Overseerr)

Handle user-submitted media requests.

```python
# View pending requests
pending = overseerr_requests(operation="pending")
for r in pending['data'].get('results', []):
    print(f"Request #{r.get('id')}: {r.get('media', {}).get('title')}")

# Approve a request
overseerr_requests(operation="approve", request_id=42)

# Create a new request
result = overseerr_requests(
    operation="create",
    media_type="movie",
    media_id=438631  # TMDB ID
)
print(result['message'])
```

### Tutorial 10: Manage Subtitles (Bazarr)

Search and download subtitles for your media.

```python
# Check what subtitles are wanted/missing
wanted = bazarr_subtitles(operation="wanted")
print(f"Items missing subtitles: {wanted['message']}")

# Search for subtitles
subs = bazarr_subtitles(operation="search", movie_id=42, language="en")
for sub in subs['data']:
    print(f"  {sub.get('name')} — {sub.get('score')}%")

# Download subtitles
bazarr_subtitles(
    operation="download",
    movie_id=42,
    subtitle_path=subs['data'][0]['path'],
    language="en"
)
```

### Tutorial 11: Agentic Cross-Arr Workflows

Use natural language with LLM-powered workflow orchestration.

```python
# Multi-step workflow
result = arr_agentic(
    operation="workflow",
    prompt="add The Matrix to Radarr with best quality"
)
print(result['message'])

# Natural language query
query = arr_agentic(
    operation="natural_query",
    prompt="what's my most wanted movie right now?"
)
print(query.get('data', {}).get('response', ''))
```

### Tutorial 12: Prefab UI Cards

Visual cards for health, calendar, and stats in supporting MCP clients.

```python
# Health card
arr_health_card()

# Calendar card (next 14 days)
arr_calendar_card(days=14)

# Stats card
arr_stats_card()
```

### Tutorial 13: Lidarr Music Management

Search and add music artists via Lidarr.

```python
# Look up an artist
artists = lidarr_artists(operation="lookup", term="Nine Inch Nails")
foreign_id = artists['data'][0].get('foreignArtistId')

# Add the artist
result = lidarr_artists(
    operation="add",
    foreign_artist_id=foreign_id,
    quality_profile_id=1,
    root_folder_path="/media/Music"
)

# List their albums
albums = lidarr_albums(operation="list", artist_id=result['data'].get('id'))
```

### Tutorial 14: Readarr Book Management

Search and add authors via Readarr.

```python
# Look up an author
authors = readarr_authors(operation="lookup", term="Brandon Sanderson")
foreign_id = authors['data'][0].get('foreignAuthorId')

# Add the author
result = readarr_authors(
    operation="add",
    foreign_author_id=foreign_id,
    quality_profile_id=1,
    root_folder_path="/media/Books"
)
```

### Tutorial 14: Readarr Book Management

Search and add authors via Readarr.

```python
# Look up an author
authors = readarr_authors(operation="lookup", term="Brandon Sanderson")
foreign_id = authors['data'][0].get('foreignAuthorId')

# Add the author
result = readarr_authors(
    operation="add",
    foreign_author_id=foreign_id,
    quality_profile_id=1,
    root_folder_path="/media/Books"
)
```

### Tutorial 15: Add One Exact Book (Readarr)

The book-level flow uses exact foreign IDs and a mandatory lookup round-trip.

```python
# Step 1: discover the add choices (profiles, root folders, tags, monitor modes)
options = readarr_add_options()
print(options['data']['monitor_modes'])

# Step 2: add exactly one book to an existing author
result = readarr_add_book(foreign_book_id="12345", author_id=7)
print(result['message'])

# Or add with a brand-new author (all four new-author fields required)
result = readarr_add_book(
    foreign_book_id="12345",
    foreign_author_id="6789",
    quality_profile_id=1,
    metadata_profile_id=1,
    root_folder_path="/media/Books",
    monitor="specific_book",
    search_for_new_book=True
)
```

### Tutorial 16: Safe Book Deletion (Readarr)

Deletion is dry-run first: preview, inspect, then commit.

```python
# Step 1: preview (default dry_run=True — nothing is deleted)
preview = readarr_delete_book(book_id=99)
print(preview['data']['preview'])

# Step 2: delete for real (author is always retained)
result = readarr_delete_book(book_id=99, dry_run=False)
print(result['message'])

# Step 3: also delete files from disk (confirmation flag required)
result = readarr_delete_book(
    book_id=99, dry_run=False,
    delete_files=True, confirm_delete_files=True
)

# Bulk: up to 100 IDs, preflighted before the first mutation
bulk = readarr_delete_books(book_ids=[1, 2, 3])
print(bulk['message'])
committed = readarr_delete_books(book_ids=[1, 2, 3], dry_run=False)
print(committed['data'])
```

### Tutorial 17: Sonarr Episode Monitoring

Drill from series to season to episode, then toggle monitoring.

```python
# Find the series, then its episodes
series = sonarr_series(operation="lookup", term="Severance")
series_id = series['data'][0]['id']
episodes = sonarr_episodes(operation="list", series_id=series_id, season_number=2)
for ep in episodes['data'][:3]:
    print(ep.get('episodeNumber'), ep.get('title'), ep.get('monitored'))

# Trigger a search for a missing episode
sonarr_episodes(operation="search", episode_id=episodes['data'][0]['id'])

# Monitor / unmonitor a single episode
sonarr_episodes(operation="set_monitored", episode_id=episodes['data'][0]['id'], monitored=True)
```

### Tutorial 18: Lidarr Album Control

```python
# Albums for an artist, then monitor only the essentials
albums = lidarr_albums(operation="list", artist_id=12)
for album in albums['data'][:5]:
    print(album.get('title'), album.get('monitored'))

lidarr_albums(operation="set_monitored", album_id=albums['data'][0]['id'], monitored=True)
```

### Tutorial 19: Prowlarr App Sync + History Triage

```python
# After any indexer add/update/delete, push to connected apps
prowlarr_indexers(operation="add", name="My Indexer",
                   config_contract="NewznabSettings")
prowlarr_applications(operation="sync_all")

# Who is failing? Group recent history per indexer
history = prowlarr_history(operation="by_indexer")
for indexer, events in history['data'].items():
    print(indexer, len(events))
```

### Tutorial 20: Queue and Disk Watch

```python
# Active downloads across the stack
queues = arr_stats(operation="queues")
print(queues['message'])

# Disk pressure per service root
disk = arr_stats(operation="disk")
for service, mounts in disk['data'].items():
    for mount in mounts:
        print(service, mount.get('path'), mount.get('freeSpace'))

# Wanted/missing roll-up
wanted = arr_stats(operation="summary")
for service, data in wanted['data'].items():
    print(service, "wanted:", data.get('wanted'))
```

### Tutorial 21: Media-Server Setup (Jellyfin / Plex / Emby)

```env
JELLYFIN_URL=http://localhost:8096
JELLYFIN_API_KEY=your_jellyfin_api_key
# PLEX_URL=http://localhost:32400
# PLEX_TOKEN=your_plex_token
# EMBY_URL=http://localhost:8096
# EMBY_API_KEY=your_emby_api_key
```

```python
# Probe one bridge directly before relying on orchestration
check = arr_orchestrate(operation="check_jellyfin", media_title="Dune")
print(check['message'])

# Placeholder keys (your-*-api-key-here) count as unconfigured:
# bridges skip them instead of erroring.
status = arr_orchestrate(operation="status")
print(status['data'])
```

### Tutorial 22: Docker Compose Stack

```bash
# Backend only (HTTP transport on :10938)
docker compose up -d arr-mcp

# Backend + dashboard (:10939)
docker compose --profile webapp up -d
```

Point MCP clients at `http://HOST:10938/mcp`. Inside containers `localhost`
means the container itself — use compose service names (`radarr`, `sonarr`,
…) for `*_URL` values, not `localhost`. Config comes from the repo-root
`.env`. See `docs/TROUBLESHOOTING.md` for container networking notes.

### Tutorial 23: Webapp Tour

Open `http://127.0.0.1:10939`. Dashboard shows one live card per service
(green = reachable, `not configured` + reason = expected before onboarding).
Orchestrate visualizes the request pipeline. Inspector runs any tool with
editable params against `/mcp` and shows raw JSON-RPC. Logger tails
`/api/logs/stream` live with filter/export. Chat needs a local model first:
install Ollama, `ollama pull llama3.2`, reload — the model appears in Chat
settings because the page probes `GET /api/llm/discover` on mount.

### Tutorial 24: Overseerr Users and Request Triage

```python
# Who asked for what? Resolve users, then triage pending requests
users = overseerr_users(operation="list")
print(f"{len(users['data'])} users")

pending = overseerr_requests(operation="pending")
for r in pending['data'].get('results', []):
    media = r.get('media', {})
    print(f"#{r.get('id')} {media.get('title')} by user {r.get('requestedBy', {}).get('displayName')}")

overseerr_requests(operation="decline", request_id=7)
```

### Tutorial 25: Back Up and Restore

arr-mcp itself is stateless — there is no database to dump. What matters:

1. `.env` — every service URL, API key, and flag. Copy it somewhere safe
   (private — it holds keys). This single file rebuilds the whole server side.
2. Each *arr service's own config/data directory (Radarr, Sonarr, …) — back
   those up per their docs; they hold your library, history, and settings.
3. The webapp holds only UI preferences (LLM provider/model, chat history) in
   `localStorage` — nice to keep, trivial to lose.

Restore is reinstall plus `.env` plus service data: clone, `uv sync`, drop in
`.env`, start, `arr_health(service="all")` to confirm green.

### Tutorial 26: Tauri Desktop App

The `native/` wrapper bundles the Python backend (PyInstaller sidecar) and the
webapp into one `.exe` installer: `just tauri-build`. The app starts its own
backend on `:10938`, opens the dashboard in a native window with Ctrl+Scroll
zoom, and listens for backend-status events with HTTP-poll fallback plus a
Restart Backend button. `ARR_TAURI=1` forces the sidecar into HTTP mode so the
webview always finds its backend. One process, no terminal windows, same
`/api/*` surface for agents.

### Tutorial 27: MCP Inspector Deep-Dive

Open the Inspector page, pick any tool (e.g. `prowlarr_search`), fill `query`,
execute — the page calls `/mcp` and renders raw JSON-RPC. Use it to: verify a
new service's tools appeared after configuration, learn exact parameter shapes
before scripting, and capture real response payloads for debugging. Every
`success=false` response includes the message string — paste it into Chat with
the skill preprompt loaded for a guided fix.

### Tutorial 28: Logs and SSE Triage

Logger tails `GET /api/logs/stream` live. When something fails: reproduce it,
watch the stream for the exception line, then pull the ring buffer
(`GET /api/logs?limit=50`) for the surrounding context. `arr_agentic`
sampling failures log at debug and fall back silently — raise the log level
(`ARR_LOG_LEVEL=DEBUG`) if orchestration answers feel thin. Export the
filtered view before reporting an issue; timestamps plus the failing tool name
are what maintainers need.

### Tutorial 29: The First-Week Routine

Day one: connect Radarr, confirm its Dashboard card turns green, request one
movie end to end. Day two: add Sonarr + one show, check the unified calendar.
Day three: Prowlarr indexers, `test_all`, `sync_all` to apps. Day four:
Overseerr for family requests, Bazarr for subtitles. Day five: Jellyfin bridge
so orchestration stops re-adding what you own. Thereafter: morning
`arr_health(service="all")`, glance at `arr_stats(operation="queues")` for
stalls, weekly `arr_calendar(operation="week")` for what's landing. Ten
minutes a day keeps a seven-service stack boring — boring is the goal.

### Tutorial 30: Scripted Health Monitoring
Poll the REST API on a schedule and alert on red services. Any HTTP client
works — no MCP client needed:

```python
import urllib.request, json

with urllib.request.urlopen("http://127.0.0.1:10938/api/health") as resp:
    health = json.load(resp)["data"]

red = [name for name, s in health.items() if not s.get("reachable")]
if red:
    print("DOWN:", ", ".join(f"{n} ({health[n].get('reason')})" for n in red))
else:
    print(f"All {len(health)} services reachable.")

with urllib.request.urlopen("http://127.0.0.1:10938/api/v1/diagnostics") as resp:
    diag = json.load(resp)
print("CPU:", diag["system"]["cpu_percent"], "MEM:", diag["system"]["memory_percent"])
```

Run it from Task Scheduler or cron every 15 minutes. The diagnostics endpoint
mirrors what the CUA smoke test checks, so a green script means installers and
dashboards will agree the backend is healthy.

## Keyboard Shortcuts and Accessibility

Dashboard navigation is keyboard-first: Ctrl+K focuses search on list pages
(Tools, Skills, Inbox), Ctrl+L toggles the Logger, Ctrl+H opens Help. Cards
use high-contrast zinc-200-on-zinc-900 pairings; status badges pair color with
text labels (green "Online", red "Offline") so state never depends on color
alone. The Tauri window supports Ctrl+Scroll zoom with Ctrl+0 reset for
small-screen readability. All interactive controls carry `data-testid`
attributes, which also makes scripted UI checks straightforward.

### Tutorial 31: Adopting arr-mcp on an Existing Servarr Setup

Already running Radarr/Sonarr for years? Adoption is read-first and reversible:

1. **Inventory before touching anything.** Record current library counts per
   service (their UIs show them) and screenshot quality profiles and root
   folders. This is your rollback baseline — arr-mcp never modifies service
   configuration, but a baseline ends arguments about what changed.
2. **Connect read-only first.** Fill in only `*_URL` + `*_API_KEY` + enabled,
   start the backend, and run `arr_health(service="all")` plus one `list` per
   service. Compare counts against the baseline. Nothing has been modified;
   every call so far was a GET.
3. **Trial one add through orchestration.** Request something you already own
   on Jellyfin — the pipeline should stop at stage one with "in library".
   Then request one genuinely new title and watch the queue. This exercises
   routing, profiles, and root folders with a single item at risk.
4. **Migrate family requests to Overseerr.** Point household members at
   Overseerr instead of chat messages, and triage with the Tutorial 24 flow
   for a week. Approval stays a human decision; arr-mcp only executes it.
5. **Turn on subtitles and search.** Bazarr `wanted` plus Prowlarr `test_all`
   close the two gaps long-running setups accumulate silently: missing
   subtitles and dead indexers nobody noticed.
6. **Keep the old bookmarks.** arr-mcp complements the *arr UIs; it does not
   replace them. Deep settings (custom formats, release profiles, import lists)
   still live in the native UIs. The rule of thumb: daily operations through
   arr-mcp and the dashboard, surgery through the native UI.

Rollback is deleting the checkout and revoking nothing: services keep their
own state, `.env` holds no service-side changes, and no arr-mcp call alters a
service's configuration objects — tools manage media items, never settings.
The one exception is Prowlarr app sync, which pushes indexer lists to connected
apps; run `sync_all` only when you mean to publish indexer edits.

### Tutorial 32: Household Multi-User Pattern

One backend, one Overseerr, many humans. Give each person an Overseerr user so
requests carry identity, and triage nightly: pending list, per-request media
lookup for quality (year, type, existing versions), approve or decline with a
note. Heavy downloaders get calendar context — `arr_calendar(operation="week")`
shows whether their request lands in days or months. Kids' profiles stay inside
Overseerr's own permission model; arr-mcp respects whatever Overseerr enforces
because it acts through the same API. Monthly: `arr_stats(operation="disk")`
per root folder, prune with dry-run deletes first, and review Bazarr `wanted`
so the backlog does not grow quietly. The whole pattern runs on the free local
stack — no hosted services, no accounts, no per-seat anything.

### Tutorial 33: Seasonal Library Review

Four times a year, spend half an hour: wanted/missing per service
(`arr_stats(operation="summary")`), anything stuck in queues older than a week
(retry or remove), disk headroom per root (plan the next drive before it fills),
indexer health (`test_all` plus history grouping), subtitle backlog
(`bazarr_subtitles(operation="wanted")`), and Overseerr pending older than a
month (stale requests get declined with a note). Finish with a calendar look at
the coming quarter for big releases worth pre-adding. This cadence catches the
slow failures — the indexer that died in February, the queue item stalled since
March — that daily glances miss because each day looks almost fine.

**Q: Seasonal review sounds like work. Can it be scripted?**
A: Mostly. The health poll in Tutorial 30 plus `arr_stats(operation="queues")`
and `prowlarr_history(operation="by_indexer")` cover the machine-checkable half
on a schedule; keep the human half (approvals, pruning judgment, release
planning) manual. Automation finds the candidates, you make the calls.

## Full Configuration Reference

| Variable | Default | Purpose |
|---|---|---|
| `RADARR_URL` / `RADARR_API_KEY` / `RADARR_ENABLED` | port 7878 | Movies |
| `SONARR_URL` / `SONARR_API_KEY` / `SONARR_ENABLED` | port 8989 | TV series |
| `LIDARR_URL` / `LIDARR_API_KEY` / `LIDARR_ENABLED` | port 8686 | Music |
| `PROWLARR_URL` / `PROWLARR_API_KEY` / `PROWLARR_ENABLED` | port 9696 | Indexers |
| `READARR_URL` / `READARR_API_KEY` / `READARR_ENABLED` | port 8787 | Books |
| `OVERSEERR_URL` / `OVERSEERR_API_KEY` / `OVERSEERR_ENABLED` | port 5055 | Requests |
| `BAZARR_URL` / `BAZARR_API_KEY` / `BAZARR_ENABLED` | port 6767 | Subtitles |
| `JELLYFIN_URL` / `JELLYFIN_API_KEY` | port 8096 | Jellyfin bridge |
| `PLEX_URL` / `PLEX_TOKEN` | port 32400 | Plex bridge |
| `EMBY_URL` / `EMBY_API_KEY` | port 8096 | Emby bridge |
| `ARR_MCP_TRANSPORT` | stdio | stdio, http, or sse |
| `ARR_MCP_HOST` / `ARR_MCP_PORT` / `ARR_MCP_PATH` | 127.0.0.1 / 10938 / /mcp | HTTP bind |
| `ARR_SAMPLING_BASE_URL` / `ARR_SAMPLING_MODEL` / `ARR_SAMPLING_API_KEY` | Ollama / llama3.2 | Agentic LLM |
| `ARR_LOG_LEVEL` / `ARR_TIMEOUT` | INFO / 30 | Logging, HTTP timeouts |

Set a key without a URL to trigger default-port probing. Omit a service
entirely to run without it. Full per-variable notes: `docs/CONFIGURATION.md`.

## Security Practices

Never commit `.env` (only `.env.example` with placeholders). Treat API keys
like passwords: the server never logs them and no endpoint returns them, but
your backup copies can leak — keep them out of screenshots, gists, and shared
drives. Prefer dry-runs for every delete, require the confirmation flag for
disk deletes, and keep `delete_files` false unless you mean it. When exposing
the dashboard beyond localhost, put it behind your own auth (Tailscale Serve
or a reverse proxy) — the webapp has no login.

## Troubleshooting

### "Service not configured — skipping tools"

If a service is not reachable and has no API key configured, its tools are not registered. Check:
- The service is running on its default port
- The API key is set in `.env`
- Auto-discovery: set the API key without the URL to enable port probing

### "Health check fails"

Run `arr_health(service="all")` to see which services fail. Common issues:
- Wrong port: check the service's default port
- API key mismatch: verify the key in the *arr web UI
- Firewall: ensure localhost connections are allowed

### "Operation X requires parameter Y"

All portmanteau tools use Literal types for operations. Each operation has specific required parameters documented in the return schema.

### "Book already present in Readarr"

`readarr_add_book` refuses duplicates by `foreign_book_id` and returns the
existing record. List the author's books (`readarr_books(operation="list",
author_id=N)`) to find it instead of re-adding.

### "New-author add says fields are required"

New-author adds need all four: `foreign_author_id`, `quality_profile_id`,
`metadata_profile_id`, `root_folder_path`. Run `readarr_add_options()` first
to pick real IDs — guessed IDs are the top failure cause. Alternatively pass
`author_id` to reuse an existing author's configuration (then no new-author
fields, tags, or monitor overrides are allowed).

### "Delete refused: confirm_delete_files=true is required"

File deletion is a two-key action by design: `delete_files=true` plus
`confirm_delete_files=true`, and only with `dry_run=false`. Preview first,
then commit. There is no undo for disk deletes.

### "Bulk delete deleted nothing"

`readarr_delete_books` preflights every ID before the first mutation — one bad
ID aborts the batch with zero deletions. Read `preflight_errors` in the
response, fix the IDs, and retry. A mid-run failure reports `deleted`,
`failed`, and `not_attempted` so you can resume after the failure point.

### "Monitored episode never grabs"

Episode monitoring composes with series monitoring: an unmonitored series
ignores episode flags. Check `sonarr_series(operation="get", series_id=N)`
first, enable series monitoring, then set the episode flag.

### "Indexer changes did nothing"

After `prowlarr_indexers` add/update/delete, call
`prowlarr_applications(operation="sync_all")` — connected *arr apps keep stale
indexer lists until synced.

### "Overseerr create failed"

Resolve the exact `media_id` with `overseerr_search(operation="search",
query="...")` first; guessed IDs fail. For TV, pass `seasons` explicitly.

### "Chat says no model"

The Chat page lists only models reported by `GET /api/llm/models`. Start
Ollama (`ollama serve`) or LM Studio with its server enabled, pull a model,
reload the page. The backend proxy (`POST /api/llm/chat`) is the only path —
the browser never calls providers directly, so a model visible in Ollama but
missing in Chat means the backend cannot reach the provider URL.

### "Docker: service unreachable"

Inside compose, `localhost` is the container itself. Use service names in
`*_URL` (e.g. `http://radarr:7878`). Keep the repo-root `.env` as the single
config source; the `arr-mcp` service reads it at startup.

## FAQ

**Q: Do I need all *arr services?**
A: No. Each service is optional. Unconfigured services simply skip tool registration. The server works with any subset.

**Q: How does auto-discovery work?**
A: If an API key is set but no URL, arr-mcp probes the default port for that service. If the port responds, the service URL is auto-configured.

**Q: What happens if I delete a movie with delete_files=True?**
A: The movie is removed from Radarr and its files are permanently deleted from disk.

**Q: Can I search across all indexers at once?**
A: Yes. Use `prowlarr_search(operation="search", query="...")` for unified search across all configured Prowlarr indexers.

**Q: Does arr-mcp support Jellyfin?**
A: Yes. Configure `JELLYFIN_URL` and `JELLYFIN_API_KEY` for cross-arr orchestration.

**Q: Can I approve Overseerr requests automatically?**
A: Yes. Use `overseerr_requests(operation="approve", request_id=N)`. For auto-approval, configure Overseerr's own settings.

**Q: What ports does arr-mcp use?**
A: Backend port 10938, frontend port 10939.

**Q: How do I get quick help within a session?**
A: Use `arr_help(operation="discover")` to list all tools, or `arr_help(operation="quickstart")` for a step-by-step guide.

**Q: Does Bazarr integration feed into other systems?**
A: Yes. Subtitle data from Bazarr can feed into jellyfin-mcp's RAG pipeline for downstream analysis.

**Q: How do I add a single book without adding its author?**
A: Pass `author_id` to `readarr_add_book` — it reuses that author's
configuration and only needs the book's `foreign_book_id`.

**Q: Can I delete an author?**
A: The book tools never delete authors, not even in bulk mode. Remove authors
in Readarr's own UI when you really mean it.

**Q: What is dry_run really doing?**
A: It runs the full preview path (record lookup, file enumeration, guard
checks) and returns what would happen, without mutating anything. Always
preview destructive calls first.

**Q: Which monitor mode should I pick for a new author?**
A: `specific_book` (default) monitors only the added book. `future` watches
upcoming releases, `all` takes the whole back-catalog (heavy). Call
`readarr_add_options()` to see the legal list before choosing.

**Q: Why did orchestration skip my media server?**
A: Placeholder credentials count as unconfigured, and unreachable servers
produce `<name>_error` pipeline steps instead of aborting. Check
`arr_orchestrate(operation="status")` for per-bridge state.

**Q: Prowlarr or per-arr search?**
A: Prowlarr for indexer-wide discovery across providers; per-arr `lookup` ops
when you already know the media type and want to add directly.

**Q: How do Prefab cards differ from the plain tools?**
A: Same data, visual rendering: `arr_health_card()` mirrors
`arr_health(service="all")` as a card in supporting clients (Claude Desktop,
Cursor). Plain tools return JSON for agents; cards render for humans.

**Q: Does the server phone home or need an account?**
A: No. Everything is local: *arr services, media servers, Ollama/LM Studio.
No online account exists anywhere in the setup.

**Q: How do I back up my configuration?**
A: The server is stateless — back up `.env` plus each *arr service's own
config/data directory. There is no arr-mcp database to dump.

**Q: Can two people share one Overseerr queue?**
A: Yes — triage with `overseerr_requests(operation="pending")`, resolve
requesters via `overseerr_users`, then approve/decline per request ID.

**Q: What does `arr_stats(operation="history")` show?**
A: Consolidated grab/failure history across services for spotting trends
(stalled downloaders, dead indexers) rather than single-item status.

## Glossary

- **Portmanteau tool**: one MCP tool whose `operation` parameter selects the
  action (e.g. `radarr_movies` with list/lookup/get/add/delete/update/import).
- **Dry run**: preview mode (`dry_run=true`, the default on deletes) that
  returns the full preview without mutating anything.
- **Preflight**: per-ID validation before a bulk mutation; any failure aborts
  with zero changes.
- **Orchestration**: the `arr_orchestrate` pipeline — media-server check, type
  detection, queue check, routed add.
- **Foreign ID**: the upstream provider ID (TMDB, TVDB, MusicBrainz, Goodreads
  via Readarr lookup) that pins an exact entity across searches and adds.
- **Monitor mode**: what Readarr/Sonarr/Lidarr watch for new releases on an
  author/series/artist (e.g. specific_book, future, all, none).
- **Prefab card**: a visual `prefab_ui` component returned by `*_card` tools
  (`@mcp.tool(app=True)`) for human-facing clients.
- **Sampling**: FastMCP SEP-1577 LLM delegation used by `arr_agentic`, with a
  structured no-sampling fallback when the client cannot sample.
