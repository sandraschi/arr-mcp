# Prowlarr (Indexer Backbone) — arr-mcp service guide

Central indexer hub for the whole stack. arr-mcp tools:
`prowlarr_indexers` (list, get, add, update, delete, test, test_all, schema),
`prowlarr_search` (unified query), `prowlarr_applications`
(list, get, sync, sync_all, test), `prowlarr_history`
(list, since, by_indexer). Page: `/prowlarr`.

## Install

```bash
docker compose up -d prowlarr
# …or standalone
docker run -d --name=prowlarr -p 9696:9696 \
  -v /path/to/config:/config \
  lscr.io/linuxserver/prowlarr:latest
```

First launch opens http://localhost:9696 — add indexers, add
Radarr/Sonarr/Lidarr/Readarr as Applications, then sync.

## API key

Prowlarr UI → Settings → General → API Key.

## Connect to arr-mcp

```env
PROWLARR_URL=http://localhost:9696
PROWLARR_API_KEY=<paste-key>
PROWLARR_ENABLED=true
```

## Common operations

```python
prowlarr_search(query="Dune 2021 bluray")          # all indexers at once
prowlarr_indexers(operation="test_all")            # health pass
prowlarr_applications(operation="sync_all")        # publish indexer edits
prowlarr_history(operation="by_indexer")           # spot dead indexers
```

## Troubleshooting

- Indexer edits do nothing until `sync_all` pushes them to the apps.
- New indexer kinds need their `config_contract` — fetch it with the
  `schema` operation before `add`.
