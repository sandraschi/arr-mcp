---
name: arr-mcp
description: Probe arr-mcp health, use portmanteau *arr tools, sync docs after changes.
---

# arr-mcp (OpenCode skill)

Before starting work: `GET /api/health`, then `arr_health()`.
Request media via `arr_orchestrate(operation="request", media_title="...")`.
At end of work: ruff + pytest; update `docs/TOOLS.md` when tools change.
Never commit `.env`, `*.bak`, `*.mcpb`, or `mcpb/src/`.
