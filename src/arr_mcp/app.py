"""FastMCP application — singleton, lifespan, resources, prompts.

Creates the FastMCP instance with sampling handler and lifespan management.
Follows the fleet pattern from jellyfin-mcp and plex-mcp.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastmcp import FastMCP

try:
    from fastmcp import Context
except ImportError:
    from fastmcp.server.context import Context  # legacy fallback

from arr_mcp import __version__
from arr_mcp.config import ArrConfig, SamplingConfig

logger = logging.getLogger(__name__)


class ArrSamplingHandler:
    """OpenAI-compatible sampling handler for LLM-powered tool responses."""

    def __init__(self, config: SamplingConfig) -> None:
        self.config = config

    async def __call__(
        self,
        context: Context,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        client = await self._get_client()
        payload: dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
        }
        if tools:
            payload["tools"] = tools

        resp = await client.post("/chat/completions", json=payload)
        resp.raise_for_status()
        return resp.json()

    async def _get_client(self) -> Any:
        import httpx

        headers: dict[str, str] = {}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        return httpx.AsyncClient(base_url=self.config.base_url, headers=headers, timeout=60)


def create_mcp(config: ArrConfig) -> FastMCP:
    """Build the FastMCP singleton with lifespan and configuration."""

    sampling_handler = ArrSamplingHandler(config.sampling)

    @asynccontextmanager
    async def lifespan(mcp: FastMCP):
        """Manage service client lifecycle."""
        logger.info(
            "arr-mcp starting — services: radarr=%s sonarr=%s lidarr=%s prowlarr=%s readarr=%s overseerr=%s bazarr=%s",
            config.radarr.is_configured,
            config.sonarr.is_configured,
            config.lidarr.is_configured,
            config.prowlarr.is_configured,
            config.readarr.is_configured,
            config.overseerr.is_configured,
            config.bazarr.is_configured,
        )
        try:
            yield
        finally:
            logger.info("arr-mcp shutting down")

    mcp = FastMCP(
        "arr-mcp",
        lifespan=lifespan,
        sampling_handler=sampling_handler,
        sampling_handler_behavior="fallback",
        instructions=(
            "You are arr-mcp, the unified control plane for the *arr automation stack. "
            "Use arr_health to check service status, arr_orchestrate to request media "
            "with automatic Jellyfin availability checking, and the per-arr tools "
            "(radarr_movies, sonarr_series, lidarr_artists, readarr_authors, "
            "prowlarr_search, bazarr_subtitles) for domain-specific operations. "
            "All arrs are optional — tools only appear for configured services."
        ),
        on_duplicate="replace",
        strict_input_validation=True,
    )
    # FastMCP 3.3+ removed env-adjacent kwargs from the constructor.
    # Set stateless_http and log_level via environment instead:
    #   FASTMCP_STATELESS_HTTP=1, FASTMCP_LOG_LEVEL=INFO

    # ── resources ──────────────────────────────────────────────────

    @mcp.resource("arr://config")
    def get_config_resource() -> str:
        """Return a summary of configured services."""
        services = []
        for svc, url in [
            ("Radarr", config.radarr),
            ("Sonarr", config.sonarr),
            ("Lidarr", config.lidarr),
            ("Prowlarr", config.prowlarr),
            ("Readarr", config.readarr),
            ("Overseerr", config.overseerr),
            ("Bazarr", config.bazarr),
            ("Jellyfin", config.jellyfin),
        ]:
            if url.is_configured:
                services.append(f"{svc} ({url.url})")
        if services:
            return f"arr-mcp v{__version__}\n\nConfigured services:\n" + "\n".join(f"  - {s}" for s in services)
        return f"arr-mcp v{__version__}\n\nNo services configured."

    @mcp.resource("arr://quickstart")
    def get_quickstart_resource() -> str:
        """Return quickstart guide for agents."""
        return (
            f"# arr-mcp v{__version__} Quickstart\n\n"
            "1. **Health check**: Call `arr_health` to see which services are reachable.\n"
            "2. **Search for media**: Use `radarr_movies(operation='lookup', title='...')` or `sonarr_series(operation='lookup', title='...')`.\n"
            "3. **Add media**: Use `arr_orchestrate(operation='request', title='...', media_type='movie')` — it checks Jellyfin first.\n"
            "4. **Cross-search**: `prowlarr_search(query='...')` searches all configured indexers.\n"
            "5. **Stack overview**: `arr_stats(operation='summary')` for disk, queue, and history across all arrs.\n"
            "6. **Calendar**: `arr_calendar(operation='upcoming')` for unified calendar across all arrs.\n"
        )

    @mcp.resource("arr://help")
    def get_help_resource() -> str:
        """Return tool discovery help for agents."""
        return (
            f"# arr-mcp v{__version__} Tool Reference\n\n"
            "## Per-Service Tools\n"
            "- `radarr_movies` — movie lifecycle (list, lookup, add, delete, update, import)\n"
            "- `sonarr_series` — series lifecycle (list, lookup, add, delete, update)\n"
            "- `sonarr_episodes` — episode management (list, get, search, set_monitored)\n"
            "- `lidarr_artists` — artist lifecycle (list, lookup, add, delete, update)\n"
            "- `lidarr_albums` — album management (list, get, lookup, set_monitored)\n"
            "- `readarr_authors` — author lifecycle (list, lookup, add, delete, update)\n"
            "- `readarr_books` — book management (list, get, lookup, set_monitored)\n"
            "- `prowlarr_indexers` — indexer lifecycle (list, get, add, update, delete, test)\n"
            "- `prowlarr_search` — unified search across all indexers\n"
            "- `prowlarr_applications` — connected *arr app management\n"
            "- `prowlarr_history` — indexer history and statistics\n"
            "- `bazarr_subtitles` — subtitle search, download, history\n"
            "- `overseerr_requests` — media request management (list, approve, decline)\n"
            "- `overseerr_search` — search Overseerr\n"
            "- `overseerr_users` — Overseerr user management\n"
            "## Cross-Arr Tools\n"
            "- `arr_health` — stack-wide health probe\n"
            "- `arr_orchestrate` — search & add across arrs + Jellyfin availability check\n"
            "- `arr_calendar` — unified calendar (upcoming, today, week, range)\n"
            "- `arr_stats` — consolidated statistics (summary, disk, queues, history)\n"
            "- `arr_agentic` — LLM-powered cross-arr workflows\n"
            "- `arr_help` — tool discovery and quickstart\n"
        )

    @mcp.resource("arr://capabilities")
    def get_capabilities_resource() -> str:
        """Return capabilities matrix for agents."""
        lines = [
            f"# arr-mcp v{__version__} Capabilities",
            "",
            "| Service | Reachable | Operations |",
            "|---------|-----------|------------|",
        ]
        svc_info = {
            "Radarr": ("movies", config.radarr.is_configured),
            "Sonarr": ("series, episodes", config.sonarr.is_configured),
            "Lidarr": ("artists, albums", config.lidarr.is_configured),
            "Prowlarr": ("indexers, search, applications", config.prowlarr.is_configured),
            "Readarr": ("authors, books [DEPRECATED]", config.readarr.is_configured),
            "Overseerr": ("requests, search, users", config.overseerr.is_configured),
            "Bazarr": ("subtitles", config.bazarr.is_configured),
        }
        for name, (ops, configured) in svc_info.items():
            status = "Yes" if configured else "No"
            lines.append(f"| {name} | {status} | {ops} |")
        return "\n".join(lines)

    # ── prompts ────────────────────────────────────────────────────

    @mcp.prompt()
    def orchestrate_media(title: str) -> list[dict[str, Any]]:
        """Build a prompt for requesting a media title via cross-arr orchestration."""
        return [
            {
                "role": "user",
                "content": f"I want to watch: {title}. Check Jellyfin first, then queue in the appropriate arr if not available.",
            },
            {
                "role": "assistant",
                "content": "Let me orchestrate that for you. I'll check Jellyfin and route to the correct service.",
            },
        ]

    @mcp.prompt()
    def stack_health_check() -> list[dict[str, Any]]:
        """Build a prompt for checking the health of the entire *arr stack."""
        return [
            {"role": "user", "content": "Check the health of my entire *arr stack. Which services are running?"},
            {"role": "assistant", "content": "I'll probe every configured *arr service and give you a health matrix."},
        ]

    return mcp
