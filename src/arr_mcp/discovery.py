"""Runtime discovery: Docker containers and fleet siblings.

Two fail-soft probes that make the dashboard honest on a fresh machine:

- ``detect_docker_containers()`` inspects ``docker ps`` for Servarr / media
  images and maps them to arr-mcp services (name, image, host ports, state).
  No Docker daemon means ``available: False`` — never an error.
- ``probe_fleet()`` checks the sibling media servers every fleet diagram
  mentions (plex-mcp, jellyfin-mcp) via their health endpoints so the webapp
  can deep-link instead of pretending a crossconnect exists.
"""

from __future__ import annotations

import logging
import shutil
import subprocess

logger = logging.getLogger(__name__)

# image substring → arr-mcp service key
IMAGE_TO_SERVICE: dict[str, str] = {
    "radarr": "radarr",
    "sonarr": "sonarr",
    "lidarr": "lidarr",
    "prowlarr": "prowlarr",
    "readarr": "readarr",
    "overseerr": "overseerr",
    "bazarr": "bazarr",
    "jellyfin": "jellyfin",
    "plex": "plex",
    "emby": "emby",
}

# service key → setup metadata for the webapp empty states
SERVICE_SETUP: dict[str, dict] = {
    "radarr": {
        "label": "Radarr",
        "subtitle": "Movies",
        "default_port": 7878,
        "compose_service": "radarr",
        "image": "lscr.io/linuxserver/radarr:latest",
        "env_keys": ["RADARR_URL", "RADARR_API_KEY", "RADARR_ENABLED"],
        "key_location": "Radarr UI → Settings → General → API Key",
    },
    "sonarr": {
        "label": "Sonarr",
        "subtitle": "TV Series",
        "default_port": 8989,
        "compose_service": "sonarr",
        "image": "lscr.io/linuxserver/sonarr:latest",
        "env_keys": ["SONARR_URL", "SONARR_API_KEY", "SONARR_ENABLED"],
        "key_location": "Sonarr UI → Settings → General → API Key",
    },
    "lidarr": {
        "label": "Lidarr",
        "subtitle": "Music",
        "default_port": 8686,
        "compose_service": "lidarr",
        "image": "lscr.io/linuxserver/lidarr:latest",
        "env_keys": ["LIDARR_URL", "LIDARR_API_KEY", "LIDARR_ENABLED"],
        "key_location": "Lidarr UI → Settings → General → API Key",
    },
    "prowlarr": {
        "label": "Prowlarr",
        "subtitle": "Indexer Backbone",
        "default_port": 9696,
        "compose_service": "prowlarr",
        "image": "lscr.io/linuxserver/prowlarr:latest",
        "env_keys": ["PROWLARR_URL", "PROWLARR_API_KEY", "PROWLARR_ENABLED"],
        "key_location": "Prowlarr UI → Settings → General → API Key",
    },
    "readarr": {
        "label": "Readarr",
        "subtitle": "Books",
        "default_port": 8787,
        "compose_service": "readarr",
        "image": "lscr.io/linuxserver/readarr:develop",
        "env_keys": ["READARR_URL", "READARR_API_KEY", "READARR_ENABLED"],
        "key_location": "Readarr UI → Settings → General → API Key",
    },
    "overseerr": {
        "label": "Overseerr",
        "subtitle": "Requests & Discovery",
        "default_port": 5055,
        "compose_service": "overseerr",
        "image": "sctx/overseerr:latest",
        "env_keys": ["OVERSEERR_URL", "OVERSEERR_API_KEY", "OVERSEERR_ENABLED"],
        "key_location": "Overseerr UI → Settings → General → API Key",
    },
    "bazarr": {
        "label": "Bazarr",
        "subtitle": "Subtitles",
        "default_port": 6767,
        "compose_service": "bazarr",
        "image": "lscr.io/linuxserver/bazarr:latest",
        "env_keys": ["BAZARR_URL", "BAZARR_API_KEY", "BAZARR_ENABLED"],
        "key_location": "Bazarr UI → Settings → General → API Key",
    },
}

# sibling MCP servers for the fleet section (backend health + frontend links)
FLEET_SIBLINGS: list[dict] = [
    {
        "name": "plex-mcp",
        "label": "Plex",
        "role": "Library & playback (owns the Plex server connection)",
        "backend_port": 10740,
        "frontend_port": 10741,
        "health_path": "/health",
    },
    {
        "name": "jellyfin-mcp",
        "label": "Jellyfin",
        "role": "Library & playback (owns the Jellyfin server connection)",
        "backend_port": 10934,
        "frontend_port": 10935,
        "health_path": "/health",
    },
]


def detect_docker_containers() -> dict:
    """List Servarr/media containers via ``docker ps``. Fail-soft.

    Returns ``{"available": bool, "containers": [...]}`` where each container
    carries name, image, service key, host ports, and state. Anything that
    goes wrong (no binary, no daemon, timeout) yields ``available: False``
    with a reason — the dashboard treats that as "unknown", not "down".
    """
    if shutil.which("docker") is None:
        return {"available": False, "reason": "docker not installed", "containers": []}
    try:
        proc = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}|{{.Image}}|{{.Ports}}|{{.State}}"],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"available": False, "reason": f"docker ps failed: {exc}", "containers": []}
    if proc.returncode != 0:
        return {
            "available": False,
            "reason": (proc.stderr or "docker daemon unreachable").strip(),
            "containers": [],
        }
    containers = []
    for line in proc.stdout.splitlines():
        parts = line.split("|")
        if len(parts) != 4:
            continue
        name, image, ports, state = parts
        service = _match_service(image, name)
        if service is None:
            continue
        containers.append(
            {
                "name": name,
                "image": image,
                "service": service,
                "ports": ports,
                "state": state,
                "host_port": _host_port(ports),
            }
        )
    return {"available": True, "containers": containers}


def _match_service(image: str, name: str) -> str | None:
    haystack = f"{image} {name}".lower()
    for needle, service in IMAGE_TO_SERVICE.items():
        if needle in haystack:
            return service
    return None


def _host_port(ports: str) -> int | None:
    """Parse the first host port from ``0.0.0.0:7878->7878/tcp`` style output."""
    import re

    match = re.search(r":(\d+)->", ports)
    return int(match.group(1)) if match else None


async def probe_fleet() -> dict:
    """Probe sibling media MCP servers. Every failure is data, not an error."""
    import httpx

    siblings = []
    for sibling in FLEET_SIBLINGS:
        url = f"http://127.0.0.1:{sibling['backend_port']}{sibling['health_path']}"
        entry = {
            **sibling,
            "reachable": False,
            "backend_url": f"http://127.0.0.1:{sibling['backend_port']}",
            "frontend_url": f"http://127.0.0.1:{sibling['frontend_port']}",
        }
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                resp = await client.get(url)
                entry["reachable"] = 200 <= resp.status_code < 300
                entry["status"] = resp.status_code
        except Exception as exc:
            entry["reason"] = str(exc)
        siblings.append(entry)
    return {"success": True, "siblings": siblings}
