# Radarr (Movies) — arr-mcp service guide

Movie collection manager. arr-mcp tool: `radarr_movies`
(list, lookup, get, add, delete, update, import). Page: `/radarr`.

## Install

```bash
# via this repo's stack (recommended)
docker compose up -d radarr
# …or standalone
docker run -d --name=radarr -p 7878:7878 \
  -v /path/to/config:/config -v /path/to/movies:/movies \
  lscr.io/linuxserver/radarr:latest
```

Native installers: https://radarr.video. First launch opens
http://localhost:7878 — finish the wizard, add a root folder
(`/movies` for compose), a download client, and indexers (via Prowlarr).

## API key

Radarr UI → Settings → General → API Key.

## Connect to arr-mcp

```env
RADARR_URL=http://localhost:7878
RADARR_API_KEY=<paste-key>
RADARR_ENABLED=true
```

Restart the backend. The Dashboard Radarr card turns green; `/radarr`
shows counts, wanted, queue, and disk. Key set without URL probes
port 7878 automatically.

## Common operations

```python
radarr_movies(operation="lookup", term="Dune")          # find TMDB id
radarr_movies(operation="add", tmdb_id=438631, quality_profile_id=1,
              root_folder_path="/movies", search_for_movie=True)
arr_orchestrate(operation="request", media_title="Dune", media_type="movie")
```

## Troubleshooting

- Page shows setup panel → service not configured (see above).
- `delete_files` defaults false; disk deletes need the confirmation flag.
- Empty 200 on delete is success (Servarr returns no body).
