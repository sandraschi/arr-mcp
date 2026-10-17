# Bazarr (Subtitles) — arr-mcp service guide

Subtitle automation for Sonarr/Radarr libraries. arr-mcp tool:
`bazarr_subtitles` (wanted, search, download, history, providers, languages).
Page: `/bazarr`.

## Install

```bash
docker compose up -d bazarr
# …or standalone
docker run -d --name=bazarr -p 6767:6767 \
  -v /path/to/config:/config \
  -v /path/to/movies:/movies -v /path/to/tv:/tv \
  lscr.io/linuxserver/bazarr:latest
```

First launch opens http://localhost:6767 — connect Sonarr + Radarr,
add providers (OpenSubtitles, etc.), enable languages.

## API key

Bazarr UI → Settings → General → API Key.

## Connect to arr-mcp

```env
BAZARR_URL=http://localhost:6767
BAZARR_API_KEY=<paste-key>
BAZARR_ENABLED=true
```

## Common operations

```python
bazarr_subtitles(operation="providers")             # check first on empty results
bazarr_subtitles(operation="wanted")                # missing-subs backlog
bazarr_subtitles(operation="search", movie_id=42, language="en")
```

## Troubleshooting

- Empty searches usually mean no providers configured, not missing subs.
- Retrieved subtitles can feed downstream analysis (jellyfin-mcp RAG).
