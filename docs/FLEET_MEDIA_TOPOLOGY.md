# Fleet media topology — arr-mcp, plex-mcp, jellyfin-mcp

Three servers, three jobs. This is the contract so nobody wires them twice.

| Server | Owns | Talks to | Never |
|---|---|---|---|
| **arr-mcp** (`:10938`/`:10939`) | Acquisition: Radarr, Sonarr, Lidarr, Prowlarr, Readarr, Overseerr, Bazarr | *arr APIs; Plex/Jellyfin/Emby **servers** (HTTP) for before-you-download availability checks | Reads plex-mcp/jellyfin-mcp state; shares DBs; duplicates their library logic |
| **plex-mcp** (`:10740`/`:10741`) | Plex library & playback, RAG, enrichment | Plex Media Server | Manages *arr queues (it probes Radarr/Sonarr/Lidarr health only) |
| **jellyfin-mcp** (`:10934`/`:10935`) | Jellyfin library, plugins, Live TV/DVR | Jellyfin Server | Manages *arr queues |

The fleet lane: **request** in arr-mcp (or Overseerr) → **download** via *arr
→ **watch** in Plex/Jellyfin. arr-mcp's `plex`/`jellyfin`/`emby` bridges are
thin availability clients against the media *servers*, not against the sibling
MCP servers — there is intentionally no shared state and no cross-server tool
calls on the media path.

Known overlap (do not extend): plex-mcp ships its own Servarr health probes
(`arr_client.py`) and arr-mcp ships its own Plex library search
(`plex_bridge.py`). Each stays a minimal client for its own lane; neither may
grow into the other's manager. If a workflow needs both sides, the agent calls
both MCP servers — that composition point is the client, not a new bridge.

Discovery surface: `GET /api/fleet` probes both siblings' `/health` endpoints
fail-soft and returns dashboard deep-links. The Dashboard renders them under
"Fleet media servers" with live reachable/not-running badges.
