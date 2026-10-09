# Troubleshooting — arr-mcp

## Backend won't start / port in use

`start.ps1` clears zombie processes before binding. Manually:
`GET /api/health` → expect `{"success": true}`. If `:10938` is held by a stale
`python.exe`, kill it and restart. Tauri sets `ARR_TAURI=1` to force HTTP mode.

## All tools say "not configured"

`.env` missing or still placeholder values. Copy `.env.example` → `.env`, set real
` *_URL` + `*_API_KEY` + `*_ENABLED=true` per service, restart. `arr_health()`
shows per-service `reachable`/`reason`.

## Emby (or Jellyfin/Plex) errors during orchestrate (issue #1)

Fixed: placeholder keys count as unconfigured, and an unreachable media server
yields a `<name>_error` pipeline step instead of aborting the request. If you
still see failures, check `EMBY_URL` is reachable from the backend host
(containers: use the Docker service name, not `localhost`).

## Delete reports failure but the item is gone (issue #2)

Fixed in `services/base.py`: empty 200 bodies return `{}`. If a fork still shows
`Expecting value: line 1 column 1 (char 0)`, update.

## Webapp shows "Backend unreachable" from a LAN/Tailscale tab

The frontend uses same-origin `/api/*` (vite proxy) in browsers. Direct
`:10938` calls from `http://goliath:10939` need CORS: the backend allows the
`:10939` origins plus LAN/Tailscale via regex. Inside Tauri it uses the absolute
sidecar URL. If you serve `webapp/dist` statically without a proxy, keep
same-origin by proxying `/api` and `/mcp` to `:10938`.

## Chat says "No LLM provider" / model list empty

Chat is backend-proxied: `GET /api/llm/discover` probes Ollama `:11434` and LM
Studio `:1234` **from the server**. The browser never calls providers directly.
Install/start Ollama or LM Studio on the backend host, then Refresh in Chat
settings. Custom URLs are forwarded by the backend (`base_url` override).

## Docker (issue #5)

`docker compose up arr-mcp` builds the backend (`Dockerfile`) with
`ARR_MCP_TRANSPORT=http` on `:10938`. Point the *arr URLs at the compose service
names when everything runs in Docker. Webapp: `docker compose --profile webapp
up webapp` (Vite `:10939`, proxies `/api` + `/mcp` to `arr-mcp:10938`).

## NSIS installer leaves a backend running

`native/windows/hooks.nsh` kills `arr-mcp-backend.exe` on install + uninstall.
If a sidecar survives, `POST /api/shutdown` (or the `arr_shutdown` tool) exits it
cleanly; hard fallback is `taskkill /F /IM arr-mcp-backend.exe`.
