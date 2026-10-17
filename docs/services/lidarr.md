# Lidarr (Music) — arr-mcp service guide

Music collection manager. arr-mcp tools: `lidarr_artists`
(list, lookup, get, add, delete, update), `lidarr_albums`
(list, get, lookup, set_monitored). Page: `/lidarr`.

## Install

```bash
docker compose up -d lidarr
# …or standalone
docker run -d --name=lidarr -p 8686:8686 \
  -v /path/to/config:/config -v /path/to/music:/music \
  lscr.io/linuxserver/lidarr:latest
```

First launch opens http://localhost:8686 — add a root folder
(`/music` for compose), connect MusicBrainz, add a download client.

## API key

Lidarr UI → Settings → General → API Key.

## Connect to arr-mcp

```env
LIDARR_URL=http://localhost:8686
LIDARR_API_KEY=<paste-key>
LIDARR_ENABLED=true
```

## Common operations

```python
lidarr_artists(operation="lookup", term="Nine Inch Nails")
lidarr_artists(operation="add", foreign_artist_id="<mbid>",
               quality_profile_id=1, root_folder_path="/music")
lidarr_albums(operation="list", artist_id=12)
```

## Troubleshooting

- Adds need the MusicBrainz `foreign_artist_id` from a lookup, not a name.
- Albums inherit the artist's profile/root folder; per-album monitoring
  trims back-catalog grabs.
