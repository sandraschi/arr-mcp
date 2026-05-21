"""FastMCP application — singleton, lifespan, resources, prompts.

Creates the FastMCP instance with sampling handler and lifespan management.
Follows the fleet pattern from jellyfin-mcp and plex-mcp.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastmcp import FastMCP
from fastmcp.server.context import Context

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
            "arr-mcp starting — services: radarr=%s sonarr=%s lidarr=%s prowlarr=%s readarr=%s bazarr=%s",
            config.radarr.is_configured,
            config.sonarr.is_configured,
            config.lidarr.is_configured,
            config.prowlarr.is_configured,
            config.readarr.is_configured,
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

    # ── system info resource ─────────────────────────────────────

    @mcp.resource("arr://config")
    def get_config_resource() -> str:
        """Return a summary of configured services."""
        services = []
        if config.radarr.is_configured:
            services.append(f"Radarr ({config.radarr.url})")
        if config.sonarr.is_configured:
            services.append(f"Sonarr ({config.sonarr.url})")
        if config.lidarr.is_configured:
            services.append(f"Lidarr ({config.lidarr.url})")
        if config.prowlarr.is_configured:
            services.append(f"Prowlarr ({config.prowlarr.url})")
        if config.readarr.is_configured:
            services.append(f"Readarr ({config.readarr.url})")
        if config.bazarr.is_configured:
            services.append(f"Bazarr ({config.bazarr.url})")
        if config.jellyfin.is_configured:
            services.append(f"Jellyfin ({config.jellyfin.url})")

        return (
            "arr-mcp v0.1.0\n\nConfigured services:\n" + "\n".join(f"  - {s}" for s in services)
            if services
            else "arr-mcp v0.1.0\n\nNo services configured."
        )

    # ── prompt ────────────────────────────────────────────────────

    @mcp.prompt()
    def orchestrate_media(title: str) -> list[dict[str, Any]]:
        """Build a prompt for requesting a media title."""
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

    return mcp
