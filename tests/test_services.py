"""Tests for BaseArrClient and arranged *arr service clients."""

import pytest
import pytest_asyncio

from arr_mcp.services.bazarr_service import BazarrClient
from arr_mcp.services.lidarr_service import LidarrClient
from arr_mcp.services.prowlarr_service import ProwlarrClient
from arr_mcp.services.radarr_service import RadarrClient
from arr_mcp.services.readarr_service import ReadarrClient
from arr_mcp.services.sonarr_service import SonarrClient

RADARR_URL = "http://localhost:7878"
SONARR_URL = "http://localhost:8989"
LIDARR_URL = "http://localhost:8686"
PROWLARR_URL = "http://localhost:9696"
READARR_URL = "http://localhost:8787"
BAZARR_URL = "http://localhost:6767"
API_KEY = "test-api-key"


@pytest_asyncio.fixture
async def radarr():
    client = RadarrClient(RADARR_URL, API_KEY)
    yield client
    await client.close()


@pytest_asyncio.fixture
async def sonarr():
    client = SonarrClient(SONARR_URL, API_KEY)
    yield client
    await client.close()


@pytest_asyncio.fixture
async def lidarr():
    client = LidarrClient(LIDARR_URL, API_KEY)
    yield client
    await client.close()


@pytest_asyncio.fixture
async def prowlarr():
    client = ProwlarrClient(PROWLARR_URL, API_KEY)
    yield client
    await client.close()


@pytest_asyncio.fixture
async def readarr():
    client = ReadarrClient(READARR_URL, API_KEY)
    yield client
    await client.close()


@pytest_asyncio.fixture
async def bazarr():
    client = BazarrClient(BAZARR_URL, API_KEY)
    yield client
    await client.close()


# ── BaseArrClient tests ───────────────────────────────────────────


class TestBaseArrClient:
    @pytest.mark.asyncio
    async def test_health_check(self, radarr, httpx_mock):
        httpx_mock.add_response(url=f"{RADARR_URL}/api/v3/system/status", json={"version": "5.0.0.1234"})
        status = await radarr.health_check()
        assert status["version"] == "5.0.0.1234"

    @pytest.mark.asyncio
    async def test_get_movies_empty(self, radarr, httpx_mock):
        httpx_mock.add_response(
            url=f"{RADARR_URL}/api/v3/movie",
            json=[],
        )
        movies = await radarr.get_movies()
        assert movies == []

    @pytest.mark.asyncio
    async def test_get_tags(self, radarr, httpx_mock):
        httpx_mock.add_response(
            url=f"{RADARR_URL}/api/v3/tag",
            json=[{"id": 1, "label": "hd"}],
        )
        tags = await radarr.get_tags()
        assert len(tags) == 1
        assert tags[0]["label"] == "hd"

    @pytest.mark.asyncio
    async def test_get_quality_profiles(self, radarr, httpx_mock):
        httpx_mock.add_response(
            url=f"{RADARR_URL}/api/v3/qualityprofile",
            json=[{"id": 1, "name": "HD-1080p"}],
        )
        profiles = await radarr.get_quality_profiles()
        assert profiles[0]["name"] == "HD-1080p"

    @pytest.mark.asyncio
    async def test_get_root_folders(self, radarr, httpx_mock):
        httpx_mock.add_response(
            url=f"{RADARR_URL}/api/v3/rootfolder",
            json=[{"id": 1, "path": "/movies"}],
        )
        folders = await radarr.get_root_folders()
        assert folders[0]["path"] == "/movies"

    @pytest.mark.asyncio
    async def test_trigger_command(self, radarr, httpx_mock):
        httpx_mock.add_response(
            url=f"{RADARR_URL}/api/v3/command",
            method="POST",
            json={"id": 99, "name": "RescanMovie"},
        )
        result = await radarr.trigger_command("RescanMovie", movieId=1)
        assert result["name"] == "RescanMovie"

    @pytest.mark.asyncio
    async def test_get_wanted_missing(self, radarr, httpx_mock):
        httpx_mock.add_response(
            url=f"{RADARR_URL}/api/v3/wanted/missing?page=1&pageSize=20&sortKey=title&sortDirection=ascending&monitored=true",
            json={"records": [], "totalRecords": 0},
        )
        wanted = await radarr.get_wanted_missing()
        assert wanted["totalRecords"] == 0

    @pytest.mark.asyncio
    async def test_client_close(self, radarr):
        await radarr.close()
        assert radarr._client is None or radarr._client.is_closed


# ── RadarrClient specifics ────────────────────────────────────────


class TestRadarrClient:
    @pytest.mark.asyncio
    async def test_lookup_movie(self, radarr, httpx_mock):
        httpx_mock.add_response(
            url=f"{RADARR_URL}/api/v3/movie/lookup?term=Dune",
            json=[{"title": "Dune", "tmdbId": 438631}],
        )
        results = await radarr.lookup_movie("Dune")
        assert results[0]["title"] == "Dune"

    @pytest.mark.asyncio
    async def test_get_movie(self, radarr, httpx_mock):
        httpx_mock.add_response(
            url=f"{RADARR_URL}/api/v3/movie/1",
            json={"id": 1, "title": "Dune"},
        )
        movie = await radarr.get_movie(1)
        assert movie["title"] == "Dune"

    @pytest.mark.asyncio
    async def test_add_movie(self, radarr, httpx_mock):
        httpx_mock.add_response(
            url=f"{RADARR_URL}/api/v3/movie",
            method="POST",
            json={"id": 1, "title": "Dune"},
        )
        result = await radarr.add_movie(
            tmdb_id=438631,
            title="Dune",
            quality_profile_id=1,
            root_folder_path="/movies",
        )
        assert result["title"] == "Dune"


# ── SonarrClient specifics ────────────────────────────────────────


class TestSonarrClient:
    @pytest.mark.asyncio
    async def test_lookup_series(self, sonarr, httpx_mock):
        httpx_mock.add_response(
            url=f"{SONARR_URL}/api/v3/series/lookup?term=Breaking+Bad",
            json=[{"title": "Breaking Bad", "tvdbId": 81189}],
        )
        results = await sonarr.lookup_series("Breaking Bad")
        assert results[0]["title"] == "Breaking Bad"

    @pytest.mark.asyncio
    async def test_get_episodes(self, sonarr, httpx_mock):
        httpx_mock.add_response(
            url=f"{SONARR_URL}/api/v3/episode?seriesId=1",
            json=[{"id": 1, "title": "Pilot", "seasonNumber": 1, "episodeNumber": 1}],
        )
        episodes = await sonarr.get_episodes(1)
        assert episodes[0]["title"] == "Pilot"


# ── ProwlarrClient specifics ──────────────────────────────────────


class TestProwlarrClient:
    @pytest.mark.asyncio
    async def test_search(self, prowlarr, httpx_mock):
        httpx_mock.add_response(
            url=f"{PROWLARR_URL}/api/v1/search?query=Dune+1080p&type=search&limit=50&offset=0",
            json=[{"title": "Dune.2021.1080p.mkv", "guid": "abc"}],
        )
        results = await prowlarr.search("Dune 1080p")
        assert results[0]["title"] == "Dune.2021.1080p.mkv"

    @pytest.mark.asyncio
    async def test_get_indexers(self, prowlarr, httpx_mock):
        httpx_mock.add_response(
            url=f"{PROWLARR_URL}/api/v1/indexer",
            json=[{"id": 1, "name": "NZBGeek"}],
        )
        indexers = await prowlarr.get_indexers()
        assert indexers[0]["name"] == "NZBGeek"


# ── LidarrClient specifics ────────────────────────────────────────


class TestLidarrClient:
    @pytest.mark.asyncio
    async def test_lookup_artist(self, lidarr, httpx_mock):
        httpx_mock.add_response(
            url=f"{LIDARR_URL}/api/v1/artist/lookup?term=NIN",
            json=[{"artistName": "Nine Inch Nails", "foreignArtistId": "abc-123"}],
        )
        results = await lidarr.lookup_artist("NIN")
        assert results[0]["artistName"] == "Nine Inch Nails"


# ── ReadarrClient specifics ──────────────────────────────────────


class TestReadarrClient:
    @pytest.mark.asyncio
    async def test_lookup_author(self, readarr, httpx_mock):
        httpx_mock.add_response(
            url=f"{READARR_URL}/api/v1/author/lookup?term=Sanderson",
            json=[{"authorName": "Brandon Sanderson", "foreignAuthorId": "xyz-789"}],
        )
        results = await readarr.lookup_author("Sanderson")
        assert results[0]["authorName"] == "Brandon Sanderson"


# ── BazarrClient specifics ────────────────────────────────────────


class TestBazarrClient:
    @pytest.mark.asyncio
    async def test_system_status(self, bazarr, httpx_mock):
        httpx_mock.add_response(url=f"{BAZARR_URL}/api/system/status", json={"version": "1.4.0"})
        status = await bazarr.health_check()
        assert status["version"] == "1.4.0"

    @pytest.mark.asyncio
    async def test_get_providers(self, bazarr, httpx_mock):
        httpx_mock.add_response(
            url=f"{BAZARR_URL}/api/providers",
            json=[{"name": "opensubtitles"}, {"name": "subscene"}],
        )
        providers = await bazarr.get_providers()
        assert len(providers) == 2
