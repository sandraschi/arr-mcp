"""Server entry point — imports tools, builds ASGI, starts transport.

Conditionally registers tools for each configured *arr service.  If a service
is not configured (missing URL/api key or disabled), its tools are skipped.
"""

from __future__ import annotations

import logging

from rich.logging import RichHandler

from arr_mcp.app import create_mcp
from arr_mcp.config import ArrConfig
from arr_mcp.constants import ArrServiceName
from arr_mcp.services.bazarr_service import BazarrClient
from arr_mcp.services.lidarr_service import LidarrClient
from arr_mcp.services.prowlarr_service import ProwlarrClient
from arr_mcp.services.radarr_service import RadarrClient
from arr_mcp.services.readarr_service import ReadarrClient
from arr_mcp.services.sonarr_service import SonarrClient
from arr_mcp.tools.bazarr_tools import register_bazarr_tools
from arr_mcp.tools.cross_arr_tools import register_cross_arr_tools
from arr_mcp.tools.health_tools import register_health_tools
from arr_mcp.tools.lidarr_tools import register_lidarr_tools
from arr_mcp.tools.prowlarr_tools import register_prowlarr_tools
from arr_mcp.tools.radarr_tools import register_radarr_tools
from arr_mcp.tools.readarr_tools import register_readarr_tools
from arr_mcp.tools.sonarr_tools import register_sonarr_tools
from arr_mcp.transport import run_server

logger = logging.getLogger(__name__)


def setup_logging(log_level: str = "INFO") -> None:
    handler = RichHandler(rich_tracebacks=True, markup=True)
    handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[handler],
    )
    # Suppress noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)


def main() -> None:
    """Main entry point — load config, create clients, register tools, start server."""

    config = ArrConfig.load_config()
    setup_logging(config.log_level)

    logger.info("arr-mcp v0.1.0 starting")

    # ── Build service clients ────────────────────────────────────

    radarr_client: RadarrClient | None = None
    sonarr_client: SonarrClient | None = None
    lidarr_client: LidarrClient | None = None
    prowlarr_client: ProwlarrClient | None = None
    readarr_client: ReadarrClient | None = None
    bazarr_client: BazarrClient | None = None

    if config.radarr.is_configured:
        radarr_client = RadarrClient(config.radarr.url, config.radarr.api_key, config.timeout)
        logger.info("Radarr client created (%s)", config.radarr.url)
    else:
        logger.info("Radarr not configured — tools will be skipped")

    if config.sonarr.is_configured:
        sonarr_client = SonarrClient(config.sonarr.url, config.sonarr.api_key, config.timeout)
        logger.info("Sonarr client created (%s)", config.sonarr.url)
    else:
        logger.info("Sonarr not configured — tools will be skipped")

    if config.lidarr.is_configured:
        lidarr_client = LidarrClient(config.lidarr.url, config.lidarr.api_key, config.timeout)
        logger.info("Lidarr client created (%s)", config.lidarr.url)
    else:
        logger.info("Lidarr not configured — tools will be skipped")

    if config.prowlarr.is_configured:
        prowlarr_client = ProwlarrClient(config.prowlarr.url, config.prowlarr.api_key, config.timeout)
        logger.info("Prowlarr client created (%s)", config.prowlarr.url)
    else:
        logger.info("Prowlarr not configured — tools will be skipped")

    if config.readarr.is_configured:
        readarr_client = ReadarrClient(config.readarr.url, config.readarr.api_key, config.timeout)
        logger.info("Readarr client created (%s)", config.readarr.url)
    else:
        logger.info("Readarr not configured — tools will be skipped")

    if config.bazarr.is_configured:
        bazarr_client = BazarrClient(config.bazarr.url, config.bazarr.api_key, config.timeout)
        logger.info("Bazarr client created (%s)", config.bazarr.url)
    else:
        logger.info("Bazarr not configured — tools will be skipped")

    # ── Create FastMCP instance ──────────────────────────────────

    mcp = create_mcp(config)

    # ── Register tools ───────────────────────────────────────────

    clients: dict[ArrServiceName, object] = {
        ArrServiceName.RADARR: radarr_client,
        ArrServiceName.SONARR: sonarr_client,
        ArrServiceName.LIDARR: lidarr_client,
        ArrServiceName.PROWLARR: prowlarr_client,
        ArrServiceName.READARR: readarr_client,
        ArrServiceName.BAZARR: bazarr_client,
    }

    register_radarr_tools(mcp, radarr_client)
    register_sonarr_tools(mcp, sonarr_client)
    register_lidarr_tools(mcp, lidarr_client)
    register_prowlarr_tools(mcp, prowlarr_client)
    register_readarr_tools(mcp, readarr_client)
    register_bazarr_tools(mcp, bazarr_client)
    register_cross_arr_tools(mcp, clients, config)
    register_health_tools(mcp, clients)

    registered_count = sum(1 for c in clients.values() if c is not None)
    logger.info("Registered tools for %d/%d services", registered_count, len(clients))

    # ── Start server ─────────────────────────────────────────────

    run_server(mcp, "arr-mcp")


if __name__ == "__main__":
    main()
