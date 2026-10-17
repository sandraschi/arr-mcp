"""Runtime service configuration: persistence, live clients, test probes.

The webapp Settings page manages *arr connections without touching ``.env``:

- overrides persist in ``config/arr-services.json`` (gitignored runtime data);
- at startup the file wins over environment variables;
- :class:`LiveClient` proxies resolve the current client on every call, so
  saving credentials takes effect immediately — REST, dashboard, orchestrator
  *and* MCP tools — with no backend restart;
- removing/disabling a service degrades its tools to structured
  "not configured" failures instead of vanishing them.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

STORE_FILENAME = "arr-services.json"


class NotConfiguredError(Exception):
    """Raised when a tool call reaches an unconfigured service."""


class LiveClient:
    """Proxy resolving the live client from the shared registry per call.

    Tool modules close over one of these forever; the registry entry behind
    it is swapped whenever credentials are saved or removed. Attribute
    access raises :class:`NotConfiguredError` when no client is configured,
    which every tool's broad ``except Exception`` turns into a structured
    ``{"success": False}`` response.
    """

    def __init__(self, clients: dict, name: str, label: str) -> None:
        object.__setattr__(self, "_clients", clients)
        object.__setattr__(self, "_name", name)
        object.__setattr__(self, "_label", label)

    def __getattr__(self, attr: str):
        clients = object.__getattribute__(self, "_clients")
        name = object.__getattribute__(self, "_name")
        label = object.__getattribute__(self, "_label")
        client = clients.get(name)
        if client is None:
            raise NotConfiguredError(f"{label} is not configured. Add its URL + API key in Settings → Services.")
        return getattr(client, attr)

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        name = object.__getattribute__(self, "_name")
        clients = object.__getattribute__(self, "_clients")
        return f"LiveClient({name}, configured={clients.get(name) is not None})"


def service_defs() -> dict[str, dict]:
    """Service metadata: config attr, default port, client class, label.

    Imported lazily so tests importing this module never pay for client deps.
    """
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

    return {
        "radarr": {"attr": "radarr", "port": RADARR_DEFAULT_PORT, "cls": RadarrClient, "label": "Radarr"},
        "sonarr": {"attr": "sonarr", "port": SONARR_DEFAULT_PORT, "cls": SonarrClient, "label": "Sonarr"},
        "lidarr": {"attr": "lidarr", "port": LIDARR_DEFAULT_PORT, "cls": LidarrClient, "label": "Lidarr"},
        "prowlarr": {"attr": "prowlarr", "port": PROWLARR_DEFAULT_PORT, "cls": ProwlarrClient, "label": "Prowlarr"},
        "readarr": {"attr": "readarr", "port": READARR_DEFAULT_PORT, "cls": ReadarrClient, "label": "Readarr"},
        "overseerr": {
            "attr": "overseerr",
            "port": OVERSEERR_DEFAULT_PORT,
            "cls": OverseerrClient,
            "label": "Overseerr",
        },
        "bazarr": {"attr": "bazarr", "port": BAZARR_DEFAULT_PORT, "cls": BazarrClient, "label": "Bazarr"},
    }


def store_path() -> Path:
    """Path of the JSON override file. ``ARR_SERVICES_FILE`` wins (tests)."""
    override = os.getenv("ARR_SERVICES_FILE")
    if override:
        return Path(override)
    return Path(__file__).resolve().parents[2] / "config" / STORE_FILENAME


def load_store() -> dict:
    """Read persisted overrides ({} when absent or corrupt)."""
    path = store_path()
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        if path.exists():
            logger.warning("Ignoring corrupt service store %s: %s", path, exc)
        return {}


def save_store(data: dict) -> None:
    path = store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def apply_file_overrides(config) -> set[str]:
    """Apply persisted overrides onto an ArrConfig. Returns overridden names."""
    from arr_mcp.config import ArrServiceConfig

    overridden: set[str] = set()
    for name, entry in load_store().items():
        if name not in service_defs() or not isinstance(entry, dict):
            continue
        setattr(
            config,
            service_defs()[name]["attr"],
            ArrServiceConfig(
                url=entry.get("url", ""),
                api_key=entry.get("api_key", ""),
                enabled=bool(entry.get("enabled", True)),
            ),
        )
        overridden.add(name)
    return overridden


async def probe_service(name: str, url: str, api_key: str, timeout: int = 10) -> dict:
    """Test credentials without saving. Returns reachable/version/error."""
    defs = service_defs()
    if name not in defs:
        return {"reachable": False, "error": f"Unknown service '{name}'."}
    if not url or not api_key:
        return {"reachable": False, "error": "URL and API key are required."}
    try:
        client = defs[name]["cls"](url.rstrip("/"), api_key, timeout)
        status = await client.get_system_status()
        version = status.get("version", "?") if isinstance(status, dict) else "?"
        return {"reachable": True, "version": str(version)}
    except Exception as exc:
        return {"reachable": False, "error": str(exc)}


def build_client(name: str, config):
    """Build (or rebuild) one service client from config + auto-discovery."""
    spec = service_defs()[name]
    svc_config = getattr(config, spec["attr"])
    if svc_config.is_configured:
        logger.info("%s client (re)built (%s)", spec["label"], svc_config.url)
        return spec["cls"](svc_config.url, svc_config.api_key, config.timeout)
    if svc_config.api_key and _port_open(spec["port"]):
        url = svc_config.url or f"http://127.0.0.1:{spec['port']}"
        logger.info("%s auto-discovered at %s", spec["label"], url)
        return spec["cls"](url, svc_config.api_key, config.timeout)
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
