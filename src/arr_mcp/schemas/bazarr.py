"""Bazarr response models — subtitles, languages, providers."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Provider(BaseModel):
    """A subtitle provider configured in Bazarr."""

    name: str = Field(default="", description="Provider name (e.g. opensubtitles).")
    enabled: bool = Field(default=True, description="Whether the provider is active.")
    providers: list[str] = Field(default_factory=list, description="Sub-provider names.")


class Language(BaseModel):
    """A Bazarr language profile."""

    code2: str = Field(default="", description="Two-letter language code (e.g. 'en').")
    code3: str = Field(default="", description="Three-letter code (e.g. 'eng').")
    name: str = Field(default="", description="Display name (e.g. 'English').")
    enabled: bool = Field(default=True, description="Whether the language is enabled.")
    hi: bool = Field(default=True, description="Hearing-impaired supported.")
    forced: bool = Field(default=False, description="Forced-only supported.")


class SubtitleResult(BaseModel):
    """Result from a subtitle search or download operation."""

    success: bool = Field(description="Whether the operation succeeded.")
    message: str = Field(default="", description="Human-readable summary.")
    data: list[dict[str, Any]] | dict[str, Any] = Field(default_factory=list)
