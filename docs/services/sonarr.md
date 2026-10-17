# Sonarr (TV Series) — arr-mcp service guide

TV collection manager. arr-mcp tools: `sonarr_series`
(list, lookup, get, add, delete, update), `sonarr_episodes`
(list, get, search, set_monitored). Page: `/sonarr`.

## Install

```bash
docker compose up -d sonarr
# …or standalone
docker run -d --name=sonarr -p 8989:8989 \
  -v /path/to/config:/config -v /path/to/tv:/tv \
  lscr.io/linuxserver/sonarr:latest
```

Native installers: https://sonarr.tv. First launch opens
http://localhost:8989 — add a root folder (`/tv` for compose),
a download client, and indexers (via Prowlarr).

## API key

Sonarr UI → Settings → General → API Key.

## Connect to arr-mcp

```env
SONARR_URL=http://localhost:8989
SONARR_API_KEY=<paste-key>
SONARR_ENABLED=true
```

Restart the backend. `/sonarr` shows series, wanted, queue, disk.

## Common operations

```python
sonarr_series(operation="lookup", term="Severance")
sonarr_episodes(operation="list", series_id=1, season_number=2)
sonarr_episodes(operation="search", episode_id=42)   # trigger search
arr_orchestrate(operation="request", media_title="Severance", media_type="series")
```

## Troubleshooting

- A monitored episode on an unmonitored series never grabs — enable the
  series first, then the episode flag.
- Episode search needs the episode or series id, not a title.
