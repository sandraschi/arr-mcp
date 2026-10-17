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
    async def test_status_endpoint(self, client):
        resp = await client.get("/api/status")
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert body["data"]["server"] == "arr-mcp"
        assert body["data"]["services_total"] == 7

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
            assert resp.status_code == 200
            body = resp.json()
            assert body["success"] is True
            assert body["data"]["enabled"] is False
            assert body["data"]["setup"]["default_port"] == 7878

    @pytest.mark.asyncio
    async def test_all_summaries_unconfigured(self):
        app = FastAPI()
        app.include_router(
            create_api_router(
                dict.fromkeys(("radarr", "sonarr", "lidarr", "prowlarr", "readarr", "overseerr", "bazarr"))
            )
        )
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as http_client:
            for service in ("radarr", "sonarr", "lidarr", "prowlarr", "readarr", "overseerr", "bazarr"):
                resp = await http_client.get(f"/api/{service}/summary")
                assert resp.status_code == 200, service
                assert resp.json()["data"]["enabled"] is False, service

    @pytest.mark.asyncio
    async def test_docker_endpoint_fail_soft(self, client):
        resp = await client.get("/api/docker")
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert "available" in body["data"]
        assert "containers" in body["data"]

    @pytest.mark.asyncio
    async def test_fleet_endpoint(self, client):
        resp = await client.get("/api/fleet")
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        names = [s["name"] for s in body["siblings"]]
        assert "plex-mcp" in names
        assert "jellyfin-mcp" in names

    @pytest.mark.asyncio
    async def test_orchestrate_request_validation(self, client):
        resp = await client.post("/api/orchestrate/request", json={})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_orchestrate_request_no_config(self, client):
        # api_app fixture passes no config → orderly 500, not a crash
        resp = await client.post("/api/orchestrate/request", json={"media_title": "Dune"})
        assert resp.status_code == 500

    @pytest.mark.asyncio
    async def test_list_endpoints_never_404(self):
        app = FastAPI()
        app.include_router(create_api_router({"radarr": None, "sonarr": None}))
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as http_client:
            for path in ("/api/radarr/movies", "/api/sonarr/series"):
                resp = await http_client.get(path)
                assert resp.status_code == 200, path
                body = resp.json()
                assert body["success"] is True, path
                assert body["data"] == [], path
                assert body["enabled"] is False, path

    @pytest.mark.asyncio
    async def test_docker_start_rejects_unknown_service(self, client):
        resp = await client.post("/api/docker/start", json={"service": "rm -rf /"})
        assert resp.status_code == 400

    @pytest.mark.asyncio
    async def test_docker_start_validation(self, client):
        resp = await client.post("/api/docker/start", json={})
        assert resp.status_code == 422

    @pytest.mark.asyncio
    async def test_docker_start_mocked_success(self, client, monkeypatch):
        import subprocess

        def fake_run(*args, **kwargs):
            cmd = args[0]
            assert cmd[:2] == ["docker", "compose"]
            assert cmd[2] == "-f" and cmd[4:7] == ["up", "-d", "bazarr"]
            assert kwargs.get("timeout") == 180
            return subprocess.CompletedProcess(cmd, 0, stdout="Container bazarr Started\n", stderr="")

        monkeypatch.setattr("arr_mcp.discovery.subprocess.run", fake_run)
        resp = await client.post("/api/docker/start", json={"service": "bazarr"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["success"] is True
        assert "bazarr" in body["message"]

    @pytest.mark.asyncio
    async def test_config_services_masks_keys(self, tmp_path, monkeypatch):
        from arr_mcp.config import ArrConfig

        monkeypatch.setenv("ARR_SERVICES_FILE", str(tmp_path / "services.json"))
        app = FastAPI()
        config = ArrConfig()
        app.include_router(create_api_router({"radarr": None}, config=config))
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as http_client:
            resp = await http_client.get("/api/config/services")
            assert resp.status_code == 200
            items = resp.json()["data"]
            assert len(items) == 7
            radarr = next(i for i in items if i["service"] == "radarr")
            assert radarr["key_set"] is False
            assert "api_key" not in radarr

    @pytest.mark.asyncio
    async def test_config_save_and_delete_roundtrip(self, tmp_path, monkeypatch):
        import json

        from arr_mcp.config import ArrConfig

        monkeypatch.setenv("ARR_SERVICES_FILE", str(tmp_path / "services.json"))
        app = FastAPI()
        config = ArrConfig()
        clients: dict = {"radarr": None}
        app.include_router(create_api_router(clients, config=config))
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as http_client:
            resp = await http_client.post(
                "/api/config/services",
                json={"service": "radarr", "url": "http://127.0.0.1:9", "api_key": "secret", "enabled": True},
            )
            assert resp.status_code == 200
            body = resp.json()
            assert body["success"] is True
            assert body["data"]["live"] is True  # client built (probe fails on closed port)
            assert body["data"]["probe"]["reachable"] is False
            saved = json.loads((tmp_path / "services.json").read_text(encoding="utf-8"))
            assert saved["radarr"]["api_key"] == "secret"
            assert clients["radarr"] is not None  # live without restart

            resp = await http_client.get("/api/config/services")
            radarr = next(i for i in resp.json()["data"] if i["service"] == "radarr")
            assert radarr["source"] == "file"
            assert radarr["key_set"] is True

            resp = await http_client.delete("/api/config/services/radarr")
            assert resp.status_code == 200
            assert clients["radarr"] is None  # env fallback (empty) degrades gracefully

    @pytest.mark.asyncio
    async def test_config_rejects_unknown_service(self, tmp_path, monkeypatch):
        from arr_mcp.config import ArrConfig

        monkeypatch.setenv("ARR_SERVICES_FILE", str(tmp_path / "services.json"))
        app = FastAPI()
        app.include_router(create_api_router({}, config=ArrConfig()))
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as http_client:
            resp = await http_client.post("/api/config/services", json={"service": "nope"})
            assert resp.status_code == 400
            resp = await http_client.post("/api/config/test", json={"service": "nope", "url": "x", "api_key": "y"})
            assert resp.status_code == 200
            assert resp.json()["data"]["reachable"] is False

    @pytest.mark.asyncio
    async def test_orchestrator_summary(self, client):
        resp = await client.get("/api/orchestrator/summary")
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["radarr"]["movies"] == 1
        assert body["total_wanted"] == 1
