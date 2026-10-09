"""REST API router - exposes per-service data for the webapp dashboard.

Each endpoint queries the corresponding *arr service client and returns
live summary data (counts, health, queue, disk, wanted).
"""

from __future__ import annotations

import asyncio
import collections
import json
import logging

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

OLLAMA_DEFAULT_URL = "http://127.0.0.1:11434"
LMSTUDIO_DEFAULT_URL = "http://127.0.0.1:1234"


class LlmChatRequest(BaseModel):
    provider: str = Field(default="ollama", description="ollama | lmstudio")
    base_url: str | None = Field(default=None, description="Override provider base URL (for Test buttons).")
    model: str = Field(description="Model name as listed by the provider.")
    messages: list[dict[str, str]] = Field(description="OpenAI-style [{role, content}] messages.")


class ChatRequest(BaseModel):
    message: str = Field(description="User message.")
    history: list[dict[str, str]] = Field(default_factory=list, description="Prior [{role, content}] turns.")
    personality: str | None = Field(default=None, description="Personality id (arr-expert, media-curator, ...).")
    provider: str = Field(default="ollama")
    base_url: str | None = None
    model: str | None = None


def _skill_text() -> str:
    """Load the domain skill for chat preprompts; fall back to a registry summary."""
    from pathlib import Path

    candidates = [
        Path(__file__).resolve().parents[2] / "skills" / "arr-mcp" / "SKILL.md",
        Path.cwd() / "skills" / "arr-mcp" / "SKILL.md",
    ]
    for path in candidates:
        if path.is_file():
            return path.read_text(encoding="utf-8")
    return (
        "# arr-mcp skill\n\nPer-service tools: radarr_movies, sonarr_series, sonarr_episodes, "
        "lidarr_artists, lidarr_albums, readarr_authors, readarr_books, prowlarr_indexers, "
        "prowlarr_search, prowlarr_applications, prowlarr_history, bazarr_subtitles, "
        "overseerr_requests, overseerr_search, overseerr_users. Cross-arr: arr_health, "
        "arr_orchestrate, arr_calendar, arr_stats, arr_help."
    )


async def _probe_llm(base_url: str, timeout: float = 2.0) -> bool:
    import httpx

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(f"{base_url.rstrip('/')}/api/tags")
            if resp.status_code == 200:
                return True
            resp = await client.get(f"{base_url.rstrip('/')}/v1/models")
            return resp.status_code == 200
    except Exception:
        return False


async def _forward_llm_chat(provider: str, base_url: str, model: str, messages: list[dict[str, str]]) -> str:
    """Forward a chat completion to Ollama/LM Studio server-side (keys never leave the server)."""
    import httpx

    base = base_url.rstrip("/")
    async with httpx.AsyncClient(timeout=120) as client:
        if provider == "lmstudio":
            resp = await client.post(
                f"{base}/v1/chat/completions",
                json={"model": model, "messages": messages},
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"] or ""
        # default: ollama
        resp = await client.post(
            f"{base}/api/chat",
            json={"model": model, "messages": messages, "stream": False},
        )
        resp.raise_for_status()
        data = resp.json()
        return (data.get("message") or {}).get("content", "")


def create_api_router(clients: dict, log_buffer: collections.deque | list[dict] | None = None) -> APIRouter:
    router = APIRouter(prefix="/api")

    # ── diagnostics (CUA-NSIS smoke test) ───────────────────────

    async def _diagnostics_payload() -> dict:
        try:
            import psutil

            cpu = psutil.cpu_percent()
            mem = psutil.virtual_memory().percent
            disk = psutil.disk_usage("/").percent
        except ImportError:
            cpu = mem = disk = None
        return {
            "success": True,
            "backend": {"port": 10938, "status": "running"},
            "system": {"cpu_percent": cpu, "memory_percent": mem, "disk_percent": disk},
            "tools": {"total": sum(1 for c in clients.values() if c is not None)},
            "cua_status": {"tesseract_available": False, "window_found": False},
        }

    @router.get("/diagnostics")
    async def api_diagnostics():
        return JSONResponse(content=await _diagnostics_payload())

    @router.get("/v1/diagnostics")
    async def api_diagnostics_v1():
        """Versioned alias required for CUA-NSIS smoke testing."""
        return JSONResponse(content=await _diagnostics_payload())

    # ── capabilities (webapp Tools/Skills pages) ─────────────────

    @router.get("/capabilities")
    async def api_capabilities():
        services = sorted(clients.keys())
        return JSONResponse(
            content={
                "success": True,
                "data": {
                    "server": "arr-mcp",
                    "services": services,
                    "configured": sorted(k for k, v in clients.items() if v is not None),
                    "transports": ["stdio", "http", "sse"],
                    "features": ["resources", "prompts", "prefab-cards", "sse-logs", "llm-proxy", "skills"],
                },
            }
        )

    # ── skills (Chat skill-first preprompt) ────────────────────────

    @router.get("/skills")
    async def api_skills():
        return JSONResponse(content={"success": True, "data": {"skill": _skill_text()}})

    # ── LLM provider discovery + backend chat proxy ───────────────
    # Keys never leave the server: the webapp Chat page must use these
    # endpoints, never fetch Ollama/LM Studio directly from the browser.

    @router.get("/llm/discover")
    async def api_llm_discover():
        ollama = await _probe_llm(OLLAMA_DEFAULT_URL)
        lmstudio = await _probe_llm(LMSTUDIO_DEFAULT_URL)
        return JSONResponse(content={"success": True, "data": {"ollama": ollama, "lmstudio": lmstudio}})

    @router.get("/llm/providers")
    async def api_llm_providers():
        ollama = await _probe_llm(OLLAMA_DEFAULT_URL)
        lmstudio = await _probe_llm(LMSTUDIO_DEFAULT_URL)
        return JSONResponse(
            content={
                "success": True,
                "data": {
                    "providers": [
                        {
                            "id": "ollama",
                            "label": "Ollama (local, free)",
                            "detected": ollama,
                            "default_url": OLLAMA_DEFAULT_URL,
                        },
                        {
                            "id": "lmstudio",
                            "label": "LM Studio (local, free)",
                            "detected": lmstudio,
                            "default_url": LMSTUDIO_DEFAULT_URL,
                        },
                    ]
                },
            }
        )

    @router.get("/llm/models")
    async def api_llm_models(provider: str = "ollama", base_url: str | None = None):
        import httpx

        base = (base_url or (OLLAMA_DEFAULT_URL if provider == "ollama" else LMSTUDIO_DEFAULT_URL)).rstrip("/")
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                if provider == "lmstudio":
                    resp = await client.get(f"{base}/v1/models")
                    resp.raise_for_status()
                    models = [m.get("id", "") for m in resp.json().get("data", [])]
                else:
                    resp = await client.get(f"{base}/api/tags")
                    resp.raise_for_status()
                    models = [m.get("name", "") for m in resp.json().get("models", [])]
            return JSONResponse(content={"success": True, "data": {"provider": provider, "models": models}})
        except Exception as e:
            raise HTTPException(502, f"{provider} at {base} unreachable: {e}") from e

    @router.get("/llm/onboarding")
    async def api_llm_onboarding():
        ollama = await _probe_llm(OLLAMA_DEFAULT_URL)
        lmstudio = await _probe_llm(LMSTUDIO_DEFAULT_URL)
        if ollama:
            path = "Ollama detected - pick a model in Chat settings and start asking."
        elif lmstudio:
            path = "LM Studio detected - pick a model in Chat settings and start asking."
        else:
            path = "No local LLM detected - install Ollama (http://127.0.0.1:11434) or LM Studio (http://127.0.0.1:1234), then reload."
        return JSONResponse(
            content={"success": True, "data": {"ollama": ollama, "lmstudio": lmstudio, "recommended_path": path}}
        )

    @router.post("/llm/chat")
    async def api_llm_chat(body: LlmChatRequest):
        base = body.base_url or (OLLAMA_DEFAULT_URL if body.provider == "ollama" else LMSTUDIO_DEFAULT_URL)
        try:
            reply = await _forward_llm_chat(body.provider, base, body.model, body.messages)
            return JSONResponse(content={"success": True, "data": {"reply": reply}})
        except Exception as e:
            raise HTTPException(502, f"LLM chat via {body.provider} failed: {e}") from e

    @router.post("/chat")
    async def api_chat(body: ChatRequest):
        """Skill-first chat: domain skill + personality preprompt, then backend LLM proxy."""
        personalities = {
            "arr-expert": "You are an expert in Radarr, Sonarr, Lidarr, Readarr, Prowlarr, Overseerr, Bazarr and the full *arr stack.",
            "media-curator": "You help curate media libraries with quality and organization in mind.",
            "quick-summarizer": "Keep responses brief and to the point.",
            "custom": "",
        }
        system_parts = [_skill_text()]
        if body.personality and personalities.get(body.personality):
            system_parts.append(personalities[body.personality])
        system_parts.append("Answer with the *arr stack in mind; suggest concrete tool calls where relevant.")
        messages = [{"role": "system", "content": "\n\n".join(system_parts)}]
        messages.extend(body.history[-20:])
        messages.append({"role": "user", "content": body.message})
        base = body.base_url or (OLLAMA_DEFAULT_URL if body.provider == "ollama" else LMSTUDIO_DEFAULT_URL)
        if not body.model:
            raise HTTPException(400, "model is required (pick one in Chat settings)")
        try:
            reply = await _forward_llm_chat(body.provider, base, body.model, messages)
            return JSONResponse(content={"success": True, "data": {"reply": reply}})
        except Exception as e:
            raise HTTPException(502, f"LLM chat via {body.provider} failed: {e}") from e

    # ── health check (all services) ──────────────────────────────

    @router.get("/health")
    async def api_health():
        result: dict[str, dict] = {}
        for name, client in clients.items():
            if client is None:
                result[name] = {"reachable": False, "reason": "not configured"}
                continue
            try:
                status = await client.health_check()
                result[name] = {"reachable": True, "version": status.get("version")}
            except Exception as e:
                result[name] = {"reachable": False, "reason": str(e)}
        return JSONResponse(content={"success": True, "data": result})

    # ── logs ─────────────────────────────────────────────────────

    @router.get("/logs")
    async def api_logs(limit: int = 100):
        if log_buffer is None:
            return JSONResponse(content={"success": True, "data": []})
        entries = list(log_buffer)[-limit:]
        return JSONResponse(content={"success": True, "data": entries})

    @router.get("/logs/stream")
    async def api_logs_stream(request: Request):
        """SSE endpoint for real-time log streaming."""

        async def event_generator():
            if log_buffer is None:
                yield f"data: {json.dumps({'timestamp': '', 'level': 'INFO', 'message': 'Log buffer not available'})}\n\n"
                return

            last_len = len(log_buffer)
            sent: set[str] = set()
            for entry in log_buffer:
                tag = f"{entry.get('timestamp', '')}|{entry.get('level', '')}|{entry.get('message', '')}"
                sent.add(tag)

            while True:
                try:
                    if await request.is_disconnected():
                        break
                    current_len = len(log_buffer)
                    if current_len > last_len:
                        new_entries = list(log_buffer)[last_len - current_len if last_len > 0 else 0 :]
                        for entry in new_entries:
                            tag = f"{entry.get('timestamp', '')}|{entry.get('level', '')}|{entry.get('message', '')}"
                            if tag not in sent:
                                sent.add(tag)
                                yield f"data: {json.dumps(entry)}\n\n"
                        last_len = current_len
                    await asyncio.sleep(0.5)
                except asyncio.CancelledError:
                    break

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    # ── radarr ───────────────────────────────────────────────────

    @router.get("/radarr/summary")
    async def radarr_summary():
        client = clients.get("radarr")
        if client is None:
            raise HTTPException(404, "Radarr not configured")
        try:
            movies = await client.get_movies()
            wanted = await client.get_wanted_missing()
            queue = await client.get_queue()
            disk = await client.get_diskspace()
            return {
                "success": True,
                "data": {
                    "movies": len(movies),
                    "wanted": wanted.get("totalRecords", len(wanted.get("records", []))),
                    "queue": queue.get("totalRecords", len(queue.get("records", []))),
                    "disk": disk,
                },
            }
        except Exception as e:
            raise HTTPException(502, str(e)) from e

    @router.get("/radarr/movies")
    async def radarr_movies(limit: int = 50):
        client = clients.get("radarr")
        if client is None:
            raise HTTPException(404, "Radarr not configured")
        try:
            movies = await client.get_movies()
            return {"success": True, "data": movies[:limit]}
        except Exception as e:
            raise HTTPException(502, str(e)) from e

    # ── sonarr ───────────────────────────────────────────────────

    @router.get("/sonarr/summary")
    async def sonarr_summary():
        client = clients.get("sonarr")
        if client is None:
            raise HTTPException(404, "Sonarr not configured")
        try:
            series_list = await client.get_series()
            wanted = await client.get_wanted_missing()
            queue = await client.get_queue()
            disk = await client.get_diskspace()
            return {
                "success": True,
                "data": {
                    "series": len(series_list),
                    "wanted": wanted.get("totalRecords", len(wanted.get("records", []))),
                    "queue": queue.get("totalRecords", len(queue.get("records", []))),
                    "disk": disk,
                },
            }
        except Exception as e:
            raise HTTPException(502, str(e)) from e

    @router.get("/sonarr/series")
    async def sonarr_series(limit: int = 50):
        client = clients.get("sonarr")
        if client is None:
            raise HTTPException(404, "Sonarr not configured")
        try:
            series_list = await client.get_series()
            return {"success": True, "data": series_list[:limit]}
        except Exception as e:
            raise HTTPException(502, str(e)) from e

    # ── lidarr ───────────────────────────────────────────────────

    @router.get("/lidarr/summary")
    async def lidarr_summary():
        client = clients.get("lidarr")
        if client is None:
            raise HTTPException(404, "Lidarr not configured")
        try:
            artists = await client.get_artists()
            wanted = await client.get_wanted_missing()
            queue = await client.get_queue()
            disk = await client.get_diskspace()
            return {
                "success": True,
                "data": {
                    "artists": len(artists),
                    "wanted": wanted.get("totalRecords", len(wanted.get("records", []))),
                    "queue": queue.get("totalRecords", len(queue.get("records", []))),
                    "disk": disk,
                },
            }
        except Exception as e:
            raise HTTPException(502, str(e)) from e

    # ── prowlarr ─────────────────────────────────────────────────

    @router.get("/prowlarr/summary")
    async def prowlarr_summary():
        client = clients.get("prowlarr")
        if client is None:
            raise HTTPException(404, "Prowlarr not configured")
        try:
            indexers = await client.get_indexers()
            apps = await client.get_applications()
            stats = await client.get_indexer_stats()
            return {
                "success": True,
                "data": {
                    "indexers": len(indexers),
                    "applications": len(apps),
                    "stats": stats,
                },
            }
        except Exception as e:
            raise HTTPException(502, str(e)) from e

    # ── readarr ──────────────────────────────────────────────────

    @router.get("/readarr/summary")
    async def readarr_summary():
        client = clients.get("readarr")
        if client is None:
            raise HTTPException(404, "Readarr not configured")
        try:
            authors = await client.get_authors()
            wanted = await client.get_wanted_missing()
            queue = await client.get_queue()
            disk = await client.get_diskspace()
            return {
                "success": True,
                "data": {
                    "authors": len(authors),
                    "wanted": wanted.get("totalRecords", len(wanted.get("records", []))),
                    "queue": queue.get("totalRecords", len(queue.get("records", []))),
                    "disk": disk,
                },
            }
        except Exception as e:
            raise HTTPException(502, str(e)) from e

    # ── overseerr ────────────────────────────────────────────────

    @router.get("/overseerr/summary")
    async def overseerr_summary():
        client = clients.get("overseerr")
        if client is None:
            raise HTTPException(404, "Overseerr not configured")
        try:
            requests = await client.get_requests(take=1)
            pending = await client.get_requests(take=100, request_filter="pending")
            count = await client.get_request_count()
            return {
                "success": True,
                "data": {
                    "total_requests": requests.get("pageInfo", {}).get("total", 0),
                    "pending": len(pending.get("results", [])),
                    "counts": count,
                },
            }
        except Exception as e:
            raise HTTPException(502, str(e)) from e

    # ── bazarr ───────────────────────────────────────────────────

    @router.get("/bazarr/summary")
    async def bazarr_summary():
        client = clients.get("bazarr")
        if client is None:
            raise HTTPException(404, "Bazarr not configured")
        try:
            wanted = await client.get_all_wanted()
            movies_wanted = len(wanted.get("movies", {}).get("data", []))
            episodes_wanted = len(wanted.get("episodes", {}).get("data", []))
            providers = await client.get_providers()
            return {
                "success": True,
                "data": {
                    "movies_wanted": movies_wanted,
                    "episodes_wanted": episodes_wanted,
                    "total_wanted": movies_wanted + episodes_wanted,
                    "providers": len(providers),
                },
            }
        except Exception as e:
            raise HTTPException(502, str(e)) from e

    # ── orchestrator summary ─────────────────────────────────────

    @router.get("/orchestrator/summary")
    async def orchestrator_summary():
        result: dict[str, dict] = {}
        total_wanted = 0

        summary_targets = [
            ("radarr", "movies", "get_movies", "get_wanted_missing"),
            ("sonarr", "series", "get_series", "get_wanted_missing"),
            ("lidarr", "artists", "get_artists", "get_wanted_missing"),
            ("readarr", "authors", "get_authors", "get_wanted_missing"),
        ]

        for name, label, list_method, wanted_method in summary_targets:
            client = clients.get(name)
            if client is None:
                result[name] = {"enabled": False, label: 0, "wanted": 0}
                continue
            try:
                items = await getattr(client, list_method)()
                wanted = await getattr(client, wanted_method)()
                count = len(items)
                wanted_count = wanted.get("totalRecords", len(wanted.get("records", [])))
                total_wanted += wanted_count
                result[name] = {"enabled": True, label: count, "wanted": wanted_count}
            except Exception as e:
                result[name] = {"enabled": True, label: 0, "wanted": 0, "error": str(e)}

        return {
            "success": True,
            "data": result,
            "total_wanted": total_wanted,
        }

    return router
