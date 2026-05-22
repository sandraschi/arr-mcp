"""Tests for constants and enums."""

from arr_mcp.constants import (
    MEDIA_TYPE_TO_ARR,
    MEDIA_TYPE_TO_JELLYFIN_ITEM,
    ArrServiceName,
    MediaType,
    service_key,
)


class TestMediaType:
    def test_values(self):
        assert MediaType.MOVIE == "movie"
        assert MediaType.SERIES == "series"
        assert MediaType.ALBUM == "album"
        assert MediaType.BOOK == "book"

    def test_media_type_to_arr_mapping(self):
        assert MEDIA_TYPE_TO_ARR[MediaType.MOVIE] == ArrServiceName.RADARR
        assert MEDIA_TYPE_TO_ARR[MediaType.SERIES] == ArrServiceName.SONARR
        assert MEDIA_TYPE_TO_ARR[MediaType.ALBUM] == ArrServiceName.LIDARR
        assert MEDIA_TYPE_TO_ARR[MediaType.BOOK] == ArrServiceName.READARR

    def test_media_type_to_jellyfin_item(self):
        assert MEDIA_TYPE_TO_JELLYFIN_ITEM[MediaType.MOVIE] == "Movie"
        assert MEDIA_TYPE_TO_JELLYFIN_ITEM[MediaType.SERIES] == "Series"
        assert MEDIA_TYPE_TO_JELLYFIN_ITEM[MediaType.ALBUM] == "MusicAlbum"
        assert MEDIA_TYPE_TO_JELLYFIN_ITEM[MediaType.BOOK] == "Book"


class TestArrServiceName:
    def test_values(self):
        assert ArrServiceName.RADARR == "radarr"
        assert ArrServiceName.SONARR == "sonarr"
        assert ArrServiceName.LIDARR == "lidarr"
        assert ArrServiceName.PROWLARR == "prowlarr"
        assert ArrServiceName.READARR == "readarr"
        assert ArrServiceName.BAZARR == "bazarr"


class TestServiceKey:
    def test_normalizes_enum(self):
        assert service_key(ArrServiceName.RADARR) == "radarr"

    def test_passes_through_string(self):
        assert service_key("sonarr") == "sonarr"
