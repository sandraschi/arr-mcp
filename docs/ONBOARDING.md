# Onboarding — arr-mcp

Get from zero to "request a movie" in ~10 minutes.

## 1. What you need (money / accounts: none)

arr-mcp itself is free (MIT). The *arr services are free; indexers you add in
Prowlarr may be paid (up to you). A local LLM is optional: Ollama and LM Studio
are both free. No online account is required anywhere.

## 2. Install

```powershell
git clone https://github.com/sandraschi/arr-mcp
cd arr-mcp
Copy-Item .env.example .env
C:\Users\sandr\.local\bin\uv.exe sync
```

Or double-click `start.bat`, or run `arr-mcp-start.bat` from the Fleet Starts
launcher. Backend `:10938`, frontend `:10939`.

## 3. Connect your first service (the big red button equivalent)

1. Install Radarr (or use the compose stack: `docker compose up -d radarr`).
2. Radarr UI → Settings → General → copy the API key.
3. In `.env`: `RADARR_URL=http://localhost:7878`, `RADARR_API_KEY=<key>`, `RADARR_ENABLED=true`.
4. Restart the backend. Dashboard card for Radarr turns green.
5. Repeat per service. Media servers (Jellyfin/Plex/Emby) are optional but make
   `arr_orchestrate` smart (already-in-library checks).

Pitfalls: placeholder keys (`your-*-api-key-here`) count as **unconfigured**;
`localhost` inside Docker means the container itself — use compose service names.

## 4. Sanity check

- `GET http://127.0.0.1:10938/api/health` → `{"success": true, ...}`.
- Dashboard shows `X/Y reachable`.
- `arr_orchestrate(operation="status")` in your MCP client lists services.
- Chat: install Ollama, pull any model (`ollama pull llama3.2`), open Chat →
  model appears → ask "which services are reachable?".

## 5. Next steps

`docs/CONFIGURATION.md` (every env var), `docs/TOOLS.md` (every tool),
`skills/arr-mcp/SKILL.md` (agent playbook). Until a service is connected, its
Dashboard card shows `not configured` with the reason — that is the expected
pre-onboarding state, not an error.
