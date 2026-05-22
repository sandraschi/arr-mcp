"""Extended mock clients for MCP tool tests."""

from __future__ import annotations

from tests.conftest import MockArrClient


class MockSonarrClient(MockArrClient):
    async def get_series(self) -> list[dict]:
        return [{"id": 1, "title": "Breaking Bad"}]

    async def lookup_series(self, term: str) -> list[dict]:
        return [{"title": "Breaking Bad", "tvdbId": 81189}]

    async def get_episodes(self, series_id: int, season_number: int | None = None) -> list[dict]:
        return [{"id": 10, "title": "Pilot", "seriesId": series_id}]

    async def get_episode(self, episode_id: int) -> dict:
        return {"id": episode_id, "title": "Pilot"}


class MockLidarrClient(MockArrClient):
    async def get_artists(self) -> list[dict]:
        return [{"id": 1, "artistName": "Nine Inch Nails"}]

    async def lookup_artist(self, term: str) -> list[dict]:
        return [{"artistName": "Nine Inch Nails", "foreignArtistId": "abc-123"}]

    async def get_albums(self, artist_id: int | None = None) -> list[dict]:
        return [{"id": 2, "title": "The Downward Spiral"}]

    async def lookup_album(self, term: str) -> list[dict]:
        return [{"title": "The Downward Spiral"}]


class MockProwlarrClient(MockArrClient):
    async def get_indexers(self) -> list[dict]:
        return [{"id": 1, "name": "NZBGeek"}]

    async def search(self, query: str, **kwargs) -> list[dict]:
        return [{"title": f"{query}.1080p.mkv", "guid": "abc"}]

    async def get_applications(self) -> list[dict]:
        return [{"id": 1, "name": "Radarr"}]

    async def get_history(self, **kwargs) -> list[dict]:
        return [{"eventType": "indexerQuery"}]


class MockReadarrClient(MockArrClient):
    async def get_authors(self) -> list[dict]:
        return [{"id": 1, "authorName": "Brandon Sanderson"}]

    async def lookup_author(self, term: str) -> list[dict]:
        return [{"authorName": "Brandon Sanderson", "foreignAuthorId": "xyz-789"}]

    async def get_books(self, author_id: int | None = None) -> list[dict]:
        return [{"id": 2, "title": "Mistborn"}]

    async def lookup_book(self, term: str) -> list[dict]:
        return [{"title": "Mistborn"}]


class MockOverseerrClient:
    async def get_requests(self, take: int = 20, skip: int = 0, request_filter: str = "all") -> dict:
        return {"results": [{"id": 1, "status": 2}], "pageInfo": {"total": 1}}

    async def get_request(self, request_id: int) -> dict:
        return {"id": request_id, "status": 2}

    async def get_request_count(self) -> dict:
        return {"pending": 1, "approved": 2}

    async def search(self, query: str, page: int = 1) -> dict:
        return {"results": [{"id": 438631, "title": query}]}

    async def get_users(self, take: int = 20) -> dict:
        return {"results": [{"id": 1, "displayName": "Admin"}]}

    async def get_user_requests(self, user_id: int) -> list[dict]:
        return [{"id": 1}]


class MockBazarrClient:
    async def get_all_wanted(self) -> dict:
        return {"movies": {"data": [{"id": 1, "title": "Dune"}]}, "episodes": {"data": []}}

    async def get_providers(self) -> list[dict]:
        return [{"name": "opensubtitles"}]

    async def get_languages(self) -> list[dict]:
        return [{"code2": "en", "name": "English"}]

    async def get_history(self) -> list[dict]:
        return [{"action": "download"}]

    async def search_subtitles(self, **kwargs) -> list[dict]:
        return [{"path": "/subs/eng.srt"}]

    async def download_subtitle(self, **kwargs) -> dict:
        return {"success": True}
