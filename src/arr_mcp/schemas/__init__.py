"""Pydantic v2 response schemas for the *arr API stack.

All tools return ``ToolResult`` (or a subclass) — a standard ``{"success": bool, "message": str, "data": ...}``
envelope.  Per-service data models are in their own modules.
"""

from arr_mcp.schemas.bazarr import Language, Provider, SubtitleResult
from arr_mcp.schemas.common import (
    HealthCheckResult,
    HealthCheckResults,
    ServiceStatus,
    ToolResult,
)
from arr_mcp.schemas.lidarr import Album, Artist, ArtistListResult
from arr_mcp.schemas.orchestrate import (
    AddToArrResult,
    AvailabilityCheckResult,
    CalendarResult,
    OrchestrateResult,
    StackStatsResult,
)
from arr_mcp.schemas.prowlarr import Indexer, ProwlarrApp, ProwlarrSearchResult
from arr_mcp.schemas.radarr import Movie, MovieListResult
from arr_mcp.schemas.readarr import Author, AuthorListResult, Book
from arr_mcp.schemas.sonarr import Episode, Series, SeriesListResult

__all__ = [
    "HealthCheckResult",
    "HealthCheckResults",
    "ServiceStatus",
    "ToolResult",
    "Movie",
    "MovieListResult",
    "Series",
    "Episode",
    "SeriesListResult",
    "Artist",
    "Album",
    "ArtistListResult",
    "Author",
    "Book",
    "AuthorListResult",
    "Indexer",
    "ProwlarrApp",
    "ProwlarrSearchResult",
    "Language",
    "Provider",
    "SubtitleResult",
    "OrchestrateResult",
    "CalendarResult",
    "StackStatsResult",
    "AvailabilityCheckResult",
    "AddToArrResult",
]
