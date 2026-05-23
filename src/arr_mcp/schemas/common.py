"""Shared response models for the *arr stack."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """Standard envelope for every MCP tool response."""

    success: bool = Field(description="Whether the operation succeeded.")
    message: str = Field(default="", description="Human-readable summary.")
    data: Any = Field(default=None, description="Operation-specific payload.")

    model_config = {"arbitrary_types_allowed": True}


class ServiceStatus(BaseModel):
    """Reachability + version info for a single service."""

    reachable: bool = Field(description="Whether the service responded.")
    version: str | None = Field(default=None, description="App version string.")
    reason: str | None = Field(default=None, description="Error message if unreachable.")


class HealthCheckResult(BaseModel):
    """Per-service health probe result."""

    service: str = Field(description="Service name (radarr, sonarr, …).")
    reachable: bool = Field(description="Whether the API responded.")
    version: str | None = Field(default=None, description="Version if reachable.")
    error: str | None = Field(default=None, description="Error detail if unreachable.")


class HealthCheckResults(BaseModel):
    """Aggregated health results across the stack."""

    services: list[HealthCheckResult] = Field(description="Per-service health results.")
    total: int = Field(description="Total services checked.")
    reachable: int = Field(description="Count of reachable services.")
