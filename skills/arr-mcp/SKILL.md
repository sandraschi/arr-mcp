# arr-mcp Skill

Unified control plane for the *arr automation stack (Radarr, Sonarr, Lidarr,
Prowlarr, Readarr, Overseerr, Bazarr) with Jellyfin/Plex/Emby availability checks.

## When to use

- "Is service X down?" → `arr_health(service="radarr")` (or `"all"`).
- "I want to watch/read/listen to TITLE" → `arr_orchestrate(operation="request",
  media_title="TITLE")` — checks Jellyfin/Plex/Emby first, auto-detects the media
  type, skips titles already queued, adds to the right arr.
- "What's coming out?" → `arr_calendar(operation="upcoming")`.
- "How full are my disks / what's downloading?" → `arr_stats(operation="disk")`
  or `operation="queues"`.
- Indexer-wide search → `prowlarr_search(query="...")`, not per-arr lookups.

## Tool catalog (portmanteau tools, `operation` selects the action)

- `radarr_movies`: list, lookup, get, add, delete, update, import
- `sonarr_series`: list, lookup, get, add, delete, update
- `sonarr_episodes`: list, get, search, set_monitored
- `lidarr_artists`: list, lookup, get, add, delete, update
- `lidarr_albums`: list, get, lookup, set_monitored
- `readarr_authors`: list, lookup, get, add, delete, update
- `readarr_books`: list, get, lookup, set_monitored
- `prowlarr_indexers`: list, get, add, update, delete, test, test_all, schema
- `prowlarr_search`, `prowlarr_applications`, `prowlarr_history`
- `bazarr_subtitles`: wanted, search, download, history, providers, languages
- `overseerr_requests`: list, get, create, approve, decline, delete, count, pending
- `overseerr_search`, `overseerr_users`
- `arr_orchestrate`: request, status, check_jellyfin, check_plex, check_emby, queue
- `arr_calendar`: upcoming, today, week, range
- `arr_stats`: summary, disk, queues, history
- `arr_health`, `arr_shutdown`, `arr_help`, `arr_agentic`
- Prefab cards: `arr_health_card`, `arr_calendar_card`, `arr_stats_card`

Every tool returns `{"success", "message", "data"}` — read `message` for the
human summary, `data` for payloads.

## Workflows

### Request media (copy-shape)
1. `arr_orchestrate(operation="request", media_title="Dune", media_type="movie")`
2. If already in library → done. If already queued → report position.
3. Else confirm the `add_result` id, then `arr_calendar(operation="week")` for ETA context.

### Diagnose a red service (copy-shape)
1. `arr_health(service="sonarr")` → note `reason`.
2. `arr_stats(operation="queues")` → stalled downloads?
3. Backend logs: `GET /api/logs?limit=50`, live: `GET /api/logs/stream` (SSE).

## Troubleshooting

- Tool missing from the session (e.g. no `radarr_movies`)? That service is not
  configured — `arr_health()` shows `not configured`. Add `*_URL` + `*_API_KEY` +
  `*_ENABLED=true` to `.env` and restart.
- Placeholder keys (`your-*-api-key-here` from `.env.example`) count as
  unconfigured; media-server checks skip them instead of erroring (issue #1).
- Deletes report success with empty `data` — Servarr returns 200 with an empty
  body; the client treats that as `{}` (issue #2).
- Chat in the webapp goes through `POST /api/chat` (skill-first: this file is the
  system preprompt). Never call Ollama/LM Studio from the browser directly.

## Config

`.env` keys: `RADARR|SONARR|LIDARR|PROWLARR|READARR|OVERSEERR|BAZARR` ×
(`_URL`, `_API_KEY`, `_ENABLED`), `JELLYFIN_URL/_API_KEY`, `PLEX_URL/_TOKEN`,
`EMBY_URL/_API_KEY`, `ARR_MCP_TRANSPORT` (stdio|http|ssec), `ARR_MCP_HOST/PORT/PATH`,
`ARR_SAMPLING_BASE_URL/MODEL`, `ARR_LOG_LEVEL`, `ARR_TIMEOUT`.
Backend `:10938` (`/api/*`, `/mcp`), frontend `:10939`. Full reference:
`docs/CONFIGURATION.md`.
