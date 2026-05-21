"""Pydantic v2 configuration models for arr-mcp."""

import os
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class ArrServiceConfig(BaseModel):
    url: str = ""
    api_key: str = ""
    enabled: bool = False

    @property
    def is_configured(self) -> bool:
        return bool(self.enabled and self.url and self.api_key)


class JellyfinConfig(BaseModel):
    url: str = ""
    api_key: str = ""

    @property
    def is_configured(self) -> bool:
        return bool(self.url and self.api_key)


class MCPTransportConfig(BaseModel):
    transport: str = Field(default="stdio")
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=10938)
    path: str = Field(default="/mcp")


class SamplingConfig(BaseModel):
    base_url: str = Field(default="http://127.0.0.1:11434/v1")
    model: str = Field(default="llama3.2")
    api_key: str | None = Field(default=None)


class ArrConfig(BaseModel):
    radarr: ArrServiceConfig = Field(default_factory=ArrServiceConfig)
    sonarr: ArrServiceConfig = Field(default_factory=ArrServiceConfig)
    lidarr: ArrServiceConfig = Field(default_factory=ArrServiceConfig)
    prowlarr: ArrServiceConfig = Field(default_factory=ArrServiceConfig)
    readarr: ArrServiceConfig = Field(default_factory=ArrServiceConfig)
    overseerr: ArrServiceConfig = Field(default_factory=ArrServiceConfig)
    bazarr: ArrServiceConfig = Field(default_factory=ArrServiceConfig)
    jellyfin: JellyfinConfig = Field(default_factory=JellyfinConfig)
    transport: MCPTransportConfig = Field(default_factory=MCPTransportConfig)
    sampling: SamplingConfig = Field(default_factory=SamplingConfig)
    log_level: str = Field(default="INFO")
    timeout: int = Field(default=30)

    @field_validator("timeout", mode="before")
    @classmethod
    def validate_timeout(cls, v: str | int) -> int:
        return int(v) if v else 30

    @classmethod
    def load_config(cls, env_path: str | None = None) -> "ArrConfig":
        from dotenv import load_dotenv

        if env_path:
            load_dotenv(env_path, override=True)
        else:
            for candidate in [".env", "../.env", str(Path.home() / ".arr-mcp.env")]:
                if Path(candidate).exists():
                    load_dotenv(candidate, override=True)
                    break

        return cls(
            radarr=ArrServiceConfig(
                url=os.getenv("RADARR_URL", ""),
                api_key=os.getenv("RADARR_API_KEY", ""),
                enabled=os.getenv("RADARR_ENABLED", "false").lower() == "true",
            ),
            sonarr=ArrServiceConfig(
                url=os.getenv("SONARR_URL", ""),
                api_key=os.getenv("SONARR_API_KEY", ""),
                enabled=os.getenv("SONARR_ENABLED", "false").lower() == "true",
            ),
            lidarr=ArrServiceConfig(
                url=os.getenv("LIDARR_URL", ""),
                api_key=os.getenv("LIDARR_API_KEY", ""),
                enabled=os.getenv("LIDARR_ENABLED", "false").lower() == "true",
            ),
            prowlarr=ArrServiceConfig(
                url=os.getenv("PROWLARR_URL", ""),
                api_key=os.getenv("PROWLARR_API_KEY", ""),
                enabled=os.getenv("PROWLARR_ENABLED", "false").lower() == "true",
            ),
            readarr=ArrServiceConfig(
                url=os.getenv("READARR_URL", ""),
                api_key=os.getenv("READARR_API_KEY", ""),
                enabled=os.getenv("READARR_ENABLED", "false").lower() == "true",
            ),
            overseerr=ArrServiceConfig(
                url=os.getenv("OVERSEERR_URL", ""),
                api_key=os.getenv("OVERSEERR_API_KEY", ""),
                enabled=os.getenv("OVERSEERR_ENABLED", "false").lower() == "true",
            ),
            bazarr=ArrServiceConfig(
                url=os.getenv("BAZARR_URL", ""),
                api_key=os.getenv("BAZARR_API_KEY", ""),
                enabled=os.getenv("BAZARR_ENABLED", "false").lower() == "true",
            ),
            jellyfin=JellyfinConfig(
                url=os.getenv("JELLYFIN_URL", ""),
                api_key=os.getenv("JELLYFIN_API_KEY", ""),
            ),
            transport=MCPTransportConfig(
                transport=os.getenv("ARR_MCP_TRANSPORT", "stdio"),
                host=os.getenv("ARR_MCP_HOST", "127.0.0.1"),
                port=int(os.getenv("ARR_MCP_PORT", "10938")),
                path=os.getenv("ARR_MCP_PATH", "/mcp"),
            ),
            sampling=SamplingConfig(
                base_url=os.getenv("ARR_SAMPLING_BASE_URL", "http://127.0.0.1:11434/v1"),
                model=os.getenv("ARR_SAMPLING_MODEL", "llama3.2"),
                api_key=os.getenv("ARR_SAMPLING_API_KEY"),
            ),
            log_level=os.getenv("ARR_LOG_LEVEL", "INFO"),
            timeout=int(os.getenv("ARR_TIMEOUT", "30")),
        )
