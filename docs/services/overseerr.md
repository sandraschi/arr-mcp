# Overseerr (Requests & Discovery) — arr-mcp service guide

Family-friendly request UI in front of Radarr/Sonarr. arr-mcp tools:
`overseerr_requests` (list, get, create, approve, decline, delete, count,
pending), `overseerr_search` (query), `overseerr_users`
(list, get). Page: `/overseerr`.

## Install

```bash
docker compose up -d overseerr
# …or standalone
docker run -d --name=overseerr -p 5055:5055 \
  -v /path/to/config:/app/config \
  sctx/overseerr:latest
```

First launch opens http://localhost:5055 — the setup wizard connects
Radarr + Sonarr and Plex/Jellyfin, then generates the API key.

## API key

Overseerr UI → Settings → General → API Key (created during setup).

## Connect to arr-mcp

```env
OVERSEERR_URL=http://localhost:5055
OVERSEERR_API_KEY=<paste-key>
OVERSEERR_ENABLED=true
```

## Common operations

```python
overseerr_search(query="Dune")                      # resolve media_id first
overseerr_requests(operation="create", media_type="movie", media_id=438631)
overseerr_requests(operation="pending")             # triage queue
overseerr_requests(operation="approve", request_id=42)
```

## Troubleshooting

- `create` with a guessed id fails — always resolve via search first.
- Approval stays human; arr-mcp only executes approve/decline.
- User attribution comes from `overseerr_users`, not the request record.
