"""Cross-arr orchestration response models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AvailabilityCheckResult(BaseModel):
    """Result from a Jellyfin availability check."""

    available: bool = Field(description="Whether the item is available in Jellyfin.")
    title: str = Field(default="", description="The original title queried.")
    matched_title: str | None = Field(default=None, description="The matched Jellyfin item name.")
    media_type: str | None = Field(default=None, description="Jellyfin item type.")
    jellyfin_id: str | None = Field(default=None, description="Jellyfin item ID.")
    in_library: bool = Field(default=False, description="Whether the item exists in the library.")


class AddToArrResult(BaseModel):
    """Result from adding media to an *arr service."""

    success: bool = Field(description="Whether the add operation succeeded.")
    action: str = Field(default="", description="What was done (added_to_radarr, …).")
    media_type: str | None = Field(default=None, description="Detected media type.")
    arr: str | None = Field(default=None, description="Target service name.")
    title: str | None = Field(default=None, description="Added media title.")
    detail: dict[str, Any] | None = Field(default=None, description="Raw response from the arr.")


class OrchestrateResult(BaseModel):
    """Top-level result from ``arr_orchestrate``."""

    success: bool = Field(description="Whether the orchestration succeeded.")
    message: str = Field(default="", description="Human-readable summary.")
    pipeline: list[str] = Field(default_factory=list, description="Steps taken (jellyfin_check, type_detection, …).")
    data: dict[str, Any] = Field(default_factory=dict, description="Detailed result payload.")


class CalendarResult(BaseModel):
    """Unified calendar response across multiple arrs."""

    success: bool = Field(description="Whether the calendar fetch succeeded.")
    message: str = Field(default="", description="Human-readable summary.")
    data: dict[str, list[dict[str, Any]]] = Field(default_factory=dict, description="Per-arr calendar entries.")
    total: int = Field(default=0, description="Total entries across all services.")


class StackStatsResult(BaseModel):
    """Consolidated stack statistics."""

    success: bool = Field(description="Whether the stats fetch succeeded.")
    message: str = Field(default="", description="Human-readable summary.")
    data: dict[str, dict[str, Any]] = Field(default_factory=dict, description="Per-arr statistics.")
