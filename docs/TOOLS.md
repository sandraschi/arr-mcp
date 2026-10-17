# Tools — arr-mcp

31 MCP tools (portmanteau + single-purpose + 3 Prefab cards). Full live reference:
`arr_help` in-session, `arr://help` resource, `GET /api/skills`.

## Per-service (registered only when the service is configured)

| Tool | Operations |
|---|---|
| `radarr_movies` | list, lookup, get, add, delete, update, import |
| `sonarr_series` | list, lookup, get, add, delete, update |
| `sonarr_episodes` | list, get, search, set_monitored |
| `lidarr_artists` | list, lookup, get, add, delete, update |
| `lidarr_albums` | list, get, lookup, set_monitored |
| `readarr_authors` | list, lookup, get, add, delete, update |
| `readarr_books` | list, get, lookup, set_monitored |
| `readarr_add_book` | add one book by exact foreign ID (existing or new author) |
| `readarr_delete_book` | preview (dry_run) or delete one book, author retained |
| `readarr_delete_books` | preflight + sequential bulk delete (≤100), authors retained |
| `readarr_add_options` | list root folders, quality/metadata profiles, tags for adds |
| `prowlarr_indexers` | list, get, add, update, delete, test, test_all, schema |
| `prowlarr_search` | query |
| `prowlarr_applications` | list, get, add, update, delete, sync |
| `prowlarr_history` | list, stats |
| `bazarr_subtitles` | wanted, search, download, history, providers, languages |
| `overseerr_requests` | list, get, create, approve, decline, delete, count, pending |
| `overseerr_search` | query |
| `overseerr_users` | list, get |

## Cross-arr (the differentiator)

| Tool | Operations |
|---|---|
| `arr_orchestrate` | request, status, check_jellyfin, check_plex, check_emby, queue |
| `arr_calendar` | upcoming, today, week, range |
| `arr_stats` | summary, disk, queues, history |
| `arr_health` | all, <service> |
| `arr_shutdown` | — (graceful self-termination) |
| `arr_help` | discover, tool_info, quickstart |
| `arr_agentic` | workflow, natural_query (Context-sampled) |
| `arr_health_card`, `arr_calendar_card`, `arr_stats_card` | Prefab UI cards |

## REST (webapp, `:10938/api/*`)

`health`, `status` (uptime, version, configured count), `capabilities`, `skills`,
`diagnostics` (+ `/v1/diagnostics`), `docker` (detected Servarr containers,
fail-soft), `docker/start` (POST: start one allowlisted compose service,
no terminal needed), `fleet` (plex-mcp/jellyfin-mcp probes + dashboard links),
`logs`, `logs/stream` (SSE), per-service `*/summary` (`enabled:false` + setup
guide when unconfigured), `orchestrator/summary`, `orchestrate/request` (POST,
runs the shared request pipeline),
`llm/discover|providers|models|onboarding`, `llm/chat` (POST proxy), `chat` (POST,
skill-first), `shutdown` (POST, orderly exit).

## Resources / prompts

`arr://config`, `arr://quickstart`, `arr://help`, `arr://capabilities`;
prompts `orchestrate_media(title)`, `stack_health_check()`.
