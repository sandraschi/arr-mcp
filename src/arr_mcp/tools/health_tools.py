"""Stack-wide health check tools.

Provides a single ``arr_health`` tool that probes every configured *arr
service and returns reachability, version, and status in one response.
"""

from __future__ import annotations

import logging
from typing import Annotated, Literal

from pydantic import Field

logger = logging.getLogger(__name__)


def register_health_tools(mcp, clients: dict) -> None:
    """Register stack health tools."""

    @mcp.tool(
        annotations={"readOnlyHint": True, "destructiveHint": False},
        version="0.1.0",
    )
    async def arr_health(
        service: Annotated[
            Literal["all", "radarr", "sonarr", "lidarr", "prowlarr", "readarr", "overseerr", "bazarr"],
            Field(description="Which service to health-check, or 'all' for stack-wide probe."),
        ] = "all",
    ) -> dict:
        """Health-check the *arr stack — probes system status per service.

        ## Return Format
        {
            "success": bool,
            "message": "X/Y services reachable",
            "data": {service_name: {"reachable": bool, "version": str|None, "reason": str|None}}
        }

        ## Examples
        arr_health()
        arr_health(service="radarr")
        arr_health(service="all")
        """
        results: dict[str, dict] = {}

        targets = list(clients.items()) if service == "all" else [(service, clients.get(service))]

        for svc_name, client in targets:
            if client is None:
                results[svc_name] = {"reachable": False, "reason": "not configured"}
                continue
            try:
                status = await client.health_check()
                results[svc_name] = {
                    "reachable": True,
                    "version": status.get("version"),
                    "startup_path": status.get("startupPath"),
                    "app_data": status.get("appData"),
                }
            except Exception as e:
                logger.warning("Health check failed for %s: %s", svc_name, e)
                results[svc_name] = {"reachable": False, "reason": str(e)}

        reachable = sum(1 for v in results.values() if v.get("reachable"))
        total = len(results)
        return {
            "success": reachable > 0,
            "message": f"{reachable}/{total} services reachable",
            "data": results,
        }
