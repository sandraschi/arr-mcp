"""Server entry point — imports tools, builds ASGI, starts transport.

Conditionally registers tools for each configured *arr service.
If a service is not configured, its tools are skipped.
Auto-discovers running services on default ports when .env is sparse.
"""

from __future__ import annotations

import collections
import logging

from rich.logging import RichHandler

from arr_mcp.api import create_api_router
from arr_mcp.app import create_mcp
from arr_mcp.config import ArrConfig
from arr_mcp.constants import (
    BAZARR_DEFAULT_PORT,
    LIDARR_DEFAULT_PORT,
    OVERSEERR_DEFAULT_PORT,
    PROWLARR_DEFAULT_PORT,
    RADARR_DEFAULT_PORT,
    READARR_DEFAULT_PORT,
    SONARR_DEFAULT_PORT,
)
from arr_mcp.services.bazarr_service import BazarrClient
from arr_mcp.services.lidarr_service import LidarrClient
from arr_mcp.services.overseerr_service import OverseerrClient
from arr_mcp.services.prowlarr_service import ProwlarrClient
from arr_mcp.services.radarr_service import RadarrClient
from arr_mcp.services.readarr_service import ReadarrClient
from arr_mcp.services.sonarr_service import SonarrClient
from arr_mcp.tools.bazarr_tools import register_bazarr_tools
from arr_mcp.tools.cross_arr_tools import register_cross_arr_tools
from arr_mcp.tools.health_tools import register_health_tools
from arr_mcp.tools.lidarr_tools import register_lidarr_tools
from arr_mcp.tools.overseerr_tools import register_overseerr_tools
from arr_mcp.tools.prowlarr_tools import register_prowlarr_tools
from arr_mcp.tools.radarr_tools import register_radarr_tools
from arr_mcp.tools.readarr_tools import register_readarr_tools
from arr_mcp.tools.sonarr_tools import register_sonarr_tools
from arr_mcp.transport import run_server

logger = logging.getLogger(__name__)

LOG_BUFFER: collections.deque = collections.deque(maxlen=500)


class BufferHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        LOG_BUFFER.append(
            {
                "timestamp": self.format(record),
                "level": record.levelname,
                "message": record.getMessage(),
            }
        )


def setup_logging(log_level: str = "INFO") -> None:
    handler = RichHandler(rich_tracebacks=True, markup=True)
    handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[handler],
    )

    buf_handler = BufferHandler()
    buf_handler.setLevel(logging.DEBUG)
    buf_handler.setFormatter(logging.Formatter("%(asctime)s", datefmt="%H:%M:%S"))
    logging.getLogger().addHandler(buf_handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.WARNING)


def main() -> None:
    config = ArrConfig.load_config()
    setup_logging(config.log_level)

    logger.info("arr-mcp v0.3.0 starting")
    logger.info("Auto-discovering *arr services on default ports...")

    # ── Build service clients (with auto-discovery) ──────────────

    radarr_client = _create_client("Radarr", config.radarr, RADARR_DEFAULT_PORT, RadarrClient, config)
    sonarr_client = _create_client("Sonarr", config.sonarr, SONARR_DEFAULT_PORT, SonarrClient, config)
    lidarr_client = _create_client("Lidarr", config.lidarr, LIDARR_DEFAULT_PORT, LidarrClient, config)
    prowlarr_client = _create_client("Prowlarr", config.prowlarr, PROWLARR_DEFAULT_PORT, ProwlarrClient, config)
    readarr_client = _create_client("Readarr", config.readarr, READARR_DEFAULT_PORT, ReadarrClient, config)
    overseerr_client = _create_client("Overseerr", config.overseerr, OVERSEERR_DEFAULT_PORT, OverseerrClient, config)
    bazarr_client = _create_client("Bazarr", config.bazarr, BAZARR_DEFAULT_PORT, BazarrClient, config)

    mcp = create_mcp(config)

    clients: dict[str, object] = {
        "radarr": radarr_client,
        "sonarr": sonarr_client,
        "lidarr": lidarr_client,
        "prowlarr": prowlarr_client,
        "readarr": readarr_client,
        "overseerr": overseerr_client,
        "bazarr": bazarr_client,
    }

    register_radarr_tools(mcp, radarr_client)
    register_sonarr_tools(mcp, sonarr_client)
    register_lidarr_tools(mcp, lidarr_client)
    register_prowlarr_tools(mcp, prowlarr_client)
    register_readarr_tools(mcp, readarr_client)
    register_overseerr_tools(mcp, overseerr_client)
    register_bazarr_tools(mcp, bazarr_client)
    register_cross_arr_tools(mcp, clients, config)
    register_health_tools(mcp, clients)

    registered_count = sum(1 for c in clients.values() if c is not None)
    logger.info("Registered tools for %d/%d services", registered_count, len(clients))

    api_router = create_api_router(clients, log_buffer=LOG_BUFFER)
    run_server(mcp, "arr-mcp", api_router=api_router)


def _create_client(
    name: str,
    svc_config,
    default_port: int,
    client_cls,
    arr_config: ArrConfig,
):
    if svc_config.is_configured:
        logger.info("%s client created (%s)", name, svc_config.url)
        return client_cls(svc_config.url, svc_config.api_key, arr_config.timeout)

    discovered = _try_discover(name, default_port, client_cls, arr_config.timeout)
    if discovered:
        logger.info("%s auto-discovered on port %d", name, default_port)
        return discovered

    logger.info("%s not configured — tools will be skipped (port %d unreachable)", name, default_port)
    return None


def _try_discover(name: str, port: int, client_cls, timeout: int):
    import httpx

    url = f"http://127.0.0.1:{port}"
    try:
        resp = httpx.get(f"{url}/api", timeout=3)
        if resp.status_code == 200:
            return client_cls(url, "", timeout)
    except Exception:
        logger.debug("%s auto-discovery failed on port %d", name, port)
        pass

    try:
        resp = httpx.get(f"{url}/api/v1/system/status", timeout=3)
        if resp.status_code == 200:
            return client_cls(url, "", timeout)
    except Exception:
        logger.debug("%s auto-discovery failed on port %d", name, port)
        pass

    try:
        resp = httpx.get(f"{url}/api/v3/system/status", timeout=3)
        if resp.status_code == 200:
            return client_cls(url, "", timeout)
    except Exception:
        logger.debug("%s auto-discovery failed on port %d", name, port)
        pass

    return None


if __name__ == "__main__":
    main()
