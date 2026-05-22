"""Tests for server client creation and auto-discovery."""

from arr_mcp.config import ArrConfig, ArrServiceConfig
from arr_mcp.server import _create_client, _port_open
from arr_mcp.services.radarr_service import RadarrClient


class TestServerClientCreation:
    def test_create_client_when_fully_configured(self):
        config = ArrConfig(
            radarr=ArrServiceConfig(
                url="http://localhost:7878",
                api_key="secret",
                enabled=True,
            ),
        )
        client = _create_client("Radarr", config.radarr, 7878, RadarrClient, config)
        assert isinstance(client, RadarrClient)
        assert client.api_key == "secret"

    def test_create_client_skips_without_api_key(self, monkeypatch):
        monkeypatch.setattr("arr_mcp.server._port_open", lambda _port: True)
        config = ArrConfig()
        client = _create_client("Radarr", config.radarr, 7878, RadarrClient, config)
        assert client is None

    def test_create_client_auto_discovers_with_api_key(self, monkeypatch):
        monkeypatch.setattr("arr_mcp.server._port_open", lambda _port: True)
        config = ArrConfig(radarr=ArrServiceConfig(api_key="secret"))
        client = _create_client("Radarr", config.radarr, 7878, RadarrClient, config)
        assert isinstance(client, RadarrClient)
        assert client.base_url == "http://127.0.0.1:7878"
        assert client.api_key == "secret"

    def test_create_client_uses_configured_url_over_default(self, monkeypatch):
        monkeypatch.setattr("arr_mcp.server._port_open", lambda _port: True)
        config = ArrConfig(radarr=ArrServiceConfig(url="http://nas:7878", api_key="secret"))
        client = _create_client("Radarr", config.radarr, 7878, RadarrClient, config)
        assert client.base_url == "http://nas:7878"

    def test_port_open_closed_port(self):
        assert _port_open(1) is False
