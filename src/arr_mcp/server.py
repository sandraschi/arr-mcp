"""Server entry point - imports tools, builds ASGI, starts transport.

All service tools are always registered; calls resolve the live client
through a proxy, so credentials saved in the webapp take effect immediately
with no restart. Unconfigured services answer with structured failures.
Service URLs/keys come from ``.env`` overridden by ``config/arr-services.json``
(managed in Settings → Services). Auto-discovers services on default ports
when an API key is set.
"""

from __future__ import annotations

import collections
import logging

from rich.console import Console
from rich.logging import RichHandler

from arr_mcp import __version__
from arr_mcp.api import create_api_router
from arr_mcp.app import create_mcp
from arr_mcp.config import ArrConfig
from arr_mcp.service_store import LiveClient, apply_file_overrides, service_defs
from arr_mcp.tools.agentic import register_agentic_tools
from arr_mcp.tools.bazarr_tools import register_bazarr_tools
from arr_mcp.tools.cross_arr_tools import register_cross_arr_tools
from arr_mcp.tools.health_tools import register_health_tools
from arr_mcp.tools.help_tools import register_help_tools
from arr_mcp.tools.lidarr_tools import register_lidarr_tools
from arr_mcp.tools.overseerr_tools import register_overseerr_tools
from arr_mcp.tools.prefab_tools import register_prefab_tools
from arr_mcp.tools.prowlarr_tools import register_prowlarr_tools
from arr_mcp.tools.radarr_tools import register_radarr_tools
from arr_mcp.tools.readarr_options import register_readarr_options
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
    handler = RichHandler(console=Console(stderr=True), rich_tracebacks=True, markup=True)
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

    logger.info("arr-mcp v%s starting", __version__)
    logger.info("Auto-discovering *arr services on default ports...")

    file_overrides = apply_file_overrides(config)
    if file_overrides:
        logger.info("Service overrides loaded from config/arr-services.json: %s", sorted(file_overrides))

    # ── Build service clients (with auto-discovery) ──────────────

    defs = service_defs()
    clients: dict[str, object] = {}
    for name, spec in defs.items():
        svc_config = getattr(config, spec["attr"])
        clients[name] = _create_client(spec["label"], svc_config, spec["port"], spec["cls"], config)

    mcp = create_mcp(config)

    # Live proxies: tools resolve the current client per call, so saving
    # credentials in the webapp takes effect with no restart.
    live = {name: LiveClient(clients, name, defs[name]["label"]) for name in defs}

    register_radarr_tools(mcp, live["radarr"])
    register_sonarr_tools(mcp, live["sonarr"])
    register_lidarr_tools(mcp, live["lidarr"])
    register_prowlarr_tools(mcp, live["prowlarr"])
    register_readarr_tools(mcp, live["readarr"])
    register_readarr_options(mcp, live["readarr"])
    register_overseerr_tools(mcp, live["overseerr"])
    register_bazarr_tools(mcp, live["bazarr"])
    register_cross_arr_tools(mcp, clients, config)
    register_health_tools(mcp, clients)
    register_help_tools(mcp)
    register_agentic_tools(mcp, clients)
    register_prefab_tools(mcp, clients)

    registered_count = sum(1 for c in clients.values() if c is not None)
    logger.info("Clients configured for %d/%d services", registered_count, len(clients))

    api_router = create_api_router(clients, log_buffer=LOG_BUFFER, config=config)
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

    if svc_config.api_key and _port_open(default_port):
        url = svc_config.url or f"http://127.0.0.1:{default_port}"
        logger.info("%s auto-discovered at %s (env API key)", name, url)
        return client_cls(url, svc_config.api_key, arr_config.timeout)

    logger.info(
        "%s not configured (port %d unreachable or missing API key) - add it in Settings → Services",
        name,
        default_port,
    )
    return None


def _port_open(port: int) -> bool:
    import socket

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex(("127.0.0.1", port))
        sock.close()
        return result == 0
    except OSError:
        return False


if __name__ == "__main__":
    main()
