"""Tests for REST API routes used by the webapp."""

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from arr_mcp.api import create_api_router
from tests.conftest import MockArrClient


@pytest.fixture
def api_app():
    clients = {
        "radarr": MockArrClient(
            movies=[{"id": 1, "title": "Dune"}],
            wanted_records=[{"title": "Missing Movie"}],
            queue_records=[{"title": "Downloading"}],
        ),
        "sonarr": None,
        "lidarr": None,
        "prowlarr": None,
        "readarr": None,
        "overseerr": None,
        "bazarr": None,
    }
    app = FastAPI()
    app.include_router(create_api_router(clients, log_buffer=[{"level": "INFO", "message": "started"}]))
    return app


@pytest.fixture
async def client(api_app):
    transport = ASGITransport(app=api_app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client


class TestApiRouter:
    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        resp = await client.get("/api/health")
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["radarr"]["reachable"] is True
        assert body["data"]["sonarr"]["reachable"] is False

    @pytest.mark.asyncio
    async def test_logs_endpoint(self, client):
        resp = await client.get("/api/logs")
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"][0]["message"] == "started"

    @pytest.mark.asyncio
    async def test_radarr_summary(self, client):
        resp = await client.get("/api/radarr/summary")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["movies"] == 1
        assert data["wanted"] == 1
        assert data["queue"] == 1

    @pytest.mark.asyncio
    async def test_radarr_movies(self, client):
        resp = await client.get("/api/radarr/movies")
        assert resp.status_code == 200
        assert resp.json()["data"][0]["title"] == "Dune"

    @pytest.mark.asyncio
    async def test_radarr_not_configured(self, api_app):
        app = FastAPI()
        app.include_router(create_api_router({"radarr": None}))
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as http_client:
            resp = await http_client.get("/api/radarr/summary")
            assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_orchestrator_summary(self, client):
        resp = await client.get("/api/orchestrator/summary")
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["radarr"]["movies"] == 1
        assert body["total_wanted"] == 1
