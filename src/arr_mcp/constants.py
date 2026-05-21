"""Constants for the *arr stack — ports, API versions, enums."""

from enum import StrEnum

# Default ports for each arr service
RADARR_DEFAULT_PORT = 7878
SONARR_DEFAULT_PORT = 8989
LIDARR_DEFAULT_PORT = 8686
PROWLARR_DEFAULT_PORT = 9696
READARR_DEFAULT_PORT = 8787
OVERSEERR_DEFAULT_PORT = 5055
BAZARR_DEFAULT_PORT = 6767
JELLYFIN_DEFAULT_PORT = 8096

# API base paths
RADARR_API_PATH = "/api/v3"
SONARR_API_PATH = "/api/v3"
LIDARR_API_PATH = "/api/v1"
PROWLARR_API_PATH = "/api/v1"
READARR_API_PATH = "/api/v1"
BAZARR_API_PATH = "/api"

# MCP server ports
ARR_MCP_DEFAULT_PORT = 10938

# Default timeout for HTTP requests (seconds)
DEFAULT_TIMEOUT = 30


class MediaType(StrEnum):
    MOVIE = "movie"
    SERIES = "series"
    ALBUM = "album"
    BOOK = "book"


class ProwlarrCategory(StrEnum):
    MOVIES = "2000"
    TV = "5000"
    MUSIC = "3000"
    BOOKS = "7000"
    ANIME = "5070"


class ArrServiceName(StrEnum):
    RADARR = "radarr"
    SONARR = "sonarr"
    LIDARR = "lidarr"
    PROWLARR = "prowlarr"
    READARR = "readarr"
    OVERSEERR = "overseerr"
    BAZARR = "bazarr"


# Maps media types to their corresponding arr service
MEDIA_TYPE_TO_ARR: dict[MediaType, ArrServiceName] = {
    MediaType.MOVIE: ArrServiceName.RADARR,
    MediaType.SERIES: ArrServiceName.SONARR,
    MediaType.ALBUM: ArrServiceName.LIDARR,
    MediaType.BOOK: ArrServiceName.READARR,
}

# Jellyfin item type mapping for search
MEDIA_TYPE_TO_JELLYFIN_ITEM: dict[MediaType, str] = {
    MediaType.MOVIE: "Movie",
    MediaType.SERIES: "Series",
    MediaType.ALBUM: "MusicAlbum",
    MediaType.BOOK: "Book",
}

# Command names shared across *arr instances
COMMAND_RESCAN = "RescanMovie"
COMMAND_REFRESH_SERIES = "RefreshSeries"
COMMAND_REFRESH_ARTIST = "RefreshArtist"
COMMAND_REFRESH_AUTHOR = "RefreshAuthor"
COMMAND_MOVIE_SEARCH = "MoviesSearch"
COMMAND_SERIES_SEARCH = "SeriesSearch"
COMMAND_ALBUM_SEARCH = "AlbumSearch"
COMMAND_BOOK_SEARCH = "BookSearch"
COMMAND_RSS_SYNC = "RssSync"
COMMAND_APPLICATION_SYNC = "ApplicationSync"
COMMAND_DOWNLOADED_SCAN = "DownloadedMoviesScan"
COMMAND_DOWNLOADED_EPISODES_SCAN = "DownloadedEpisodesScan"
COMMAND_MISSING_EPISODE_SEARCH = "MissingEpisodeSearch"
COMMAND_CUTOFF_UNMET_ALBUM_SEARCH = "CutoffUnmetAlbumSearch"
COMMAND_BACKUP = "Backup"
