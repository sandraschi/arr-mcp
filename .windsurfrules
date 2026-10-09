# arr-mcp — Cursor rules (tool-awareness subset; full protocol: mcp-central-docs/standards/AGENTS.md)

Stack: FastMCP >=3.4.4,<4 + FastAPI backend `:10938`, React/Vite dashboard `:10939`.
Entry: `src/arr_mcp/server.py` (`python -m arr_mcp --http --port 10938`).
Tools live in `src/arr_mcp/tools/*` (`register_*_tools`); services in `src/arr_mcp/services/`.

## Session Context (arr-mcp)

Before starting work: probe `GET /api/health`, then `arr_health()` for service state.
Sweep `rg "print\(|console\.log|TODO|FIXME"` for drift before editing.
At end of work: `uv run ruff check src/arr_mcp tests/` + `pytest -q`; update
`docs/TOOLS.md` when tools change; never commit `.env`, `*.bak`, `*.mcpb`.
