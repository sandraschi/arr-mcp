# arr-mcp — Copilot instructions

FastMCP >=3.4.4,<4 server (`src/arr_mcp/`), FastAPI backend `:10938`, React dashboard `:10939`.
Before work: check `GET /api/health` + `arr_health()`. Portmanteau tools only
(`operation: Literal[...]`). Returns are `{"success","message","data"}`. After work:
ruff + pytest, keep `docs/TOOLS.md` in sync.
