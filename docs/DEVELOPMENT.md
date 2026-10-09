# Development — arr-mcp

## Layout

`src/arr_mcp/`: `server.py` (entry, client wiring) → `app.py` (`create_mcp`,
resources, prompts) → `tools/*` (`register_*_tools(mcp, client)` per service) →
`transport.py` (stdio/http/sse runner, CORS, `/api/shutdown`) → `api.py`
(REST router for the webapp). `services/` holds httpx clients over
`services/base.py`; `utils/` holds Jellyfin/Plex/Emby bridges.

## Commands

```powershell
C:\Users\sandr\.local\bin\uv.exe sync
C:\Users\sandr\.local\bin\uv.exe run arr-mcp            # stdio
C:\Users\sandr\.local\bin\uv.exe run python -m arr_mcp --http --port 10938
C:\Users\sandr\.local\bin\uv.exe run ruff check src/arr_mcp tests/
C:\Users\sandr\.local\bin\uv.exe run ruff format src/arr_mcp tests/
C:\Users\sandr\.local\bin\uv.exe run mypy
C:\Users\sandr\.local\bin\uv.exe run pytest tests/ -q
```

`just` wrappers: `just lint|typecheck|test|e2e|ci|build-native|cua-nsis-test|cua-webapp-test|mcpb-pack`
(fleet recipes via `scripts/just/fleet.just`).

## Conventions

- Tools are portmanteaus: one `@mcp.tool` per domain with a `Literal[operations]`
  parameter (`Annotated[..., Field(description=...)]`), `annotations=`,
  `## Return Format` + `## Examples` docstrings, dialogic
  `{"success", "message", "data"}` returns, `logger.exception` in except blocks.
- No `print()` in `src/` (ruff T20 enforced); no `S110`/`S112` silencing.
- `services/base.py::_delete` tolerates empty 200 bodies (issue #2) — keep that guard.
- Bridges treat placeholder credentials as unconfigured (issue #1) — keep
  `is_placeholder_credential()` checks.
- Webapp calls the backend same-origin (`/api/*` via vite proxy); absolute backend
  URLs only behind the Tauri gate (`webapp/src/utils/api.ts`).
- Chat is backend-proxied (`POST /api/chat`, skill-first). Never fetch
  Ollama/LM Studio from the browser.

## Tests

`tests/` uses pytest + pytest-httpx (`mock_clients.py`). Add a regression test for
every fixed bug (see `test_services.py` delete-empty-body test for the pattern).
