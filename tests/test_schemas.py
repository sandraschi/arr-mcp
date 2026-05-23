"""Tests for Pydantic response schemas — import, construction, serialisation."""

from arr_mcp.schemas.bazarr import Language, Provider, SubtitleResult
from arr_mcp.schemas.common import HealthCheckResult, HealthCheckResults, ServiceStatus, ToolResult
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


class TestToolResult:
    def test_defaults(self):
        r = ToolResult(success=True)
        assert r.success is True
        assert r.message == ""

    def test_roundtrip(self):
        r = ToolResult(success=True, message="hello", data={"key": "val"})
        d = r.model_dump()
        assert d["success"] is True
        assert d["message"] == "hello"
        assert d["data"]["key"] == "val"


class TestHealthCheckModels:
    def test_service_status(self):
        s = ServiceStatus(reachable=True, version="5.0.0")
        assert s.reachable is True
        assert s.version == "5.0.0"

    def test_health_check_result(self):
        h = HealthCheckResult(service="radarr", reachable=True, version="5.0.0")
        assert h.service == "radarr"

    def test_health_check_results_aggregation(self):
        r = HealthCheckResults(
            services=[
                HealthCheckResult(service="radarr", reachable=True, version="5.0.0"),
            ],
            total=1,
            reachable=1,
        )
        assert r.reachable == 1
        assert r.total == 1


class TestRadarrModels:
    def test_movie_construction(self):
        m = Movie(id=1, title="Dune", tmdb_id=438631, year=2021)
        assert m.title == "Dune"
        assert m.tmdb_id == 438631

    def test_movie_alias(self):
        m = Movie.model_validate({"id": 1, "title": "Dune", "tmdbId": 438631})
        assert m.tmdb_id == 438631

    def test_movie_extra_ignored(self):
        m = Movie.model_validate({"id": 1, "title": "Dune", "unknownField": "ignored"})
        assert m.title == "Dune"

    def test_movie_list_result(self):
        r = MovieListResult(success=True, message="1 movie", data=[Movie(id=1, title="Dune")])
        assert r.success is True
        assert len(r.data) == 1
        assert r.data[0].title == "Dune"


class TestSonarrModels:
    def test_series_construction(self):
        s = Series(id=1, title="Breaking Bad", tvdb_id=81189)
        assert s.title == "Breaking Bad"
        assert s.tvdb_id == 81189

    def test_episode_construction(self):
        e = Episode(id=10, series_id=1, title="Pilot", season_number=1, episode_number=1)
        assert e.title == "Pilot"
        assert e.series_id == 1

    def test_series_list_result(self):
        r = SeriesListResult(
            success=True,
            message="1 series",
            data=[Series(id=1, title="Breaking Bad")],
            total=1,
        )
        assert r.total == 1


class TestLidarrModels:
    def test_artist_construction(self):
        a = Artist(id=1, artist_name="Nine Inch Nails", foreign_artist_id="abc-123")
        assert a.artist_name == "Nine Inch Nails"

    def test_album_construction(self):
        a = Album(id=2, title="The Downward Spiral", artist_id=1, album_type="Album")
        assert a.title == "The Downward Spiral"
        assert a.album_type == "Album"

    def test_artist_list_result(self):
        r = ArtistListResult(success=True, data=[Artist(id=1, artist_name="NIN")])
        assert r.success is True


class TestReadarrModels:
    def test_author_construction(self):
        a = Author(id=1, author_name="Brandon Sanderson")
        assert a.author_name == "Brandon Sanderson"

    def test_book_construction(self):
        b = Book(id=2, title="Mistborn", author_id=1, isbn="9780765311788")
        assert b.title == "Mistborn"

    def test_author_list_result(self):
        r = AuthorListResult(success=True, data=[Author(id=1, author_name="Sanderson")])
        assert r.success is True


class TestProwlarrModels:
    def test_indexer_construction(self):
        i = Indexer(id=1, name="NZBGeek", protocol="usenet", priority=25)
        assert i.name == "NZBGeek"

    def test_application_construction(self):
        a = ProwlarrApp(id=1, name="Radarr", app_type="Radarr")
        assert a.name == "Radarr"

    def test_search_result(self):
        r = ProwlarrSearchResult(title="Dune.2021.1080p.mkv", guid="abc-123", protocol="torrent", seeders=10)
        assert r.title == "Dune.2021.1080p.mkv"
        assert r.seeders == 10


class TestBazarrModels:
    def test_provider(self):
        p = Provider(name="opensubtitles", enabled=True)
        assert p.name == "opensubtitles"

    def test_language(self):
        lang = Language(code2="en", code3="eng", name="English")
        assert lang.code2 == "en"

    def test_subtitle_result(self):
        r = SubtitleResult(success=True, message="Found subtitles")
        assert r.success is True


class TestOrchestrateModels:
    def test_availability_check(self):
        r = AvailabilityCheckResult(
            available=True,
            title="Dune",
            media_type="Movie",
            in_library=True,
        )
        assert r.available is True
        assert r.in_library is True

    def test_orchestrate_result(self):
        r = OrchestrateResult(success=True, message="Done", pipeline=["jellyfin_check", "add_to_arr"])
        assert len(r.pipeline) == 2

    def test_add_to_arr_result(self):
        r = AddToArrResult(success=True, action="added_to_radarr", title="Dune")
        assert r.action == "added_to_radarr"

    def test_calendar_result(self):
        r = CalendarResult(success=True, total=5)
        assert r.total == 5

    def test_stack_stats_result(self):
        r = StackStatsResult(success=True, data={"radarr": {"movies": 42}})
        assert r.data["radarr"]["movies"] == 42
