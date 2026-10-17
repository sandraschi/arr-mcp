"""Tests for the runtime service store (Settings → Services, no .env)."""

from __future__ import annotations

import pytest

from arr_mcp.config import ArrConfig
from arr_mcp.service_store import (
    LiveClient,
    NotConfiguredError,
    apply_file_overrides,
    load_store,
    probe_service,
    save_store,
    service_defs,
)


def test_service_defs_cover_all_seven():
    defs = service_defs()
    assert set(defs) == {"radarr", "sonarr", "lidarr", "prowlarr", "readarr", "overseerr", "bazarr"}
    for _name, spec in defs.items():
        assert hasattr(ArrConfig(), spec["attr"])


def test_store_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("ARR_SERVICES_FILE", str(tmp_path / "services.json"))
    assert load_store() == {}
    save_store({"radarr": {"url": "http://localhost:7878", "api_key": "k", "enabled": True}})
    assert load_store()["radarr"]["api_key"] == "k"


def test_store_ignores_corrupt_file(tmp_path, monkeypatch):
    target = tmp_path / "services.json"
    target.write_text("{not json", encoding="utf-8")
    monkeypatch.setenv("ARR_SERVICES_FILE", str(target))
    assert load_store() == {}


def test_apply_file_overrides_beats_env(tmp_path, monkeypatch):
    monkeypatch.setenv("ARR_SERVICES_FILE", str(tmp_path / "services.json"))
    save_store({"sonarr": {"url": "http://from-file:8989", "api_key": "filekey", "enabled": True}})
    config = ArrConfig()
    assert config.sonarr.url == ""
    assert apply_file_overrides(config) == {"sonarr"}
    assert config.sonarr.url == "http://from-file:8989"
    assert config.sonarr.is_configured is True


@pytest.mark.asyncio
async def test_live_client_calls_through():
    class Fake:
        async def get_movies(self):
            return [{"title": "Dune"}]

    proxy = LiveClient({"radarr": Fake()}, "radarr", "Radarr")
    assert await proxy.get_movies() == [{"title": "Dune"}]


def test_live_client_raises_when_unconfigured():
    proxy = LiveClient({"radarr": None}, "radarr", "Radarr")
    with pytest.raises(NotConfiguredError, match="Radarr is not configured"):
        _ = proxy.get_movies


@pytest.mark.asyncio
async def test_live_client_picks_up_replacement():
    class Fake:
        def __init__(self, tag):
            self.tag = tag

        async def ping(self):
            return self.tag

    clients = {"radarr": Fake("old")}
    proxy = LiveClient(clients, "radarr", "Radarr")
    assert await proxy.ping() == "old"
    clients["radarr"] = Fake("new")
    assert await proxy.ping() == "new"


@pytest.mark.asyncio
async def test_probe_rejects_unknown_service():
    result = await probe_service("nope", "http://x", "k")
    assert result["reachable"] is False


@pytest.mark.asyncio
async def test_probe_requires_url_and_key():
    result = await probe_service("radarr", "", "")
    assert result["reachable"] is False
    assert "required" in result["error"]
