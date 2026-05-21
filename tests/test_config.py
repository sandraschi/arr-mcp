"""Tests for config loading and validation."""

from arr_mcp.config import ArrConfig, ArrServiceConfig


class TestArrServiceConfig:
    def test_default_is_not_configured(self):
        cfg = ArrServiceConfig()
        assert not cfg.is_configured

    def test_configured_when_all_set(self):
        cfg = ArrServiceConfig(url="http://localhost:7878", api_key="abc123", enabled=True)
        assert cfg.is_configured

    def test_not_configured_when_disabled(self):
        cfg = ArrServiceConfig(url="http://localhost:7878", api_key="abc123", enabled=False)
        assert not cfg.is_configured

    def test_not_configured_without_api_key(self):
        cfg = ArrServiceConfig(url="http://localhost:7878", enabled=True)
        assert not cfg.is_configured


class TestArrConfig:
    def test_load_defaults(self):
        cfg = ArrConfig()
        assert cfg.radarr.enabled is False
        assert cfg.transport.port == 10938

    def test_load_from_env(self, monkeypatch, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text("RADARR_URL=http://localhost:7878\nRADARR_API_KEY=testkey\nRADARR_ENABLED=true\n")

        cfg = ArrConfig.load_config(str(env_file))
        assert cfg.radarr.url == "http://localhost:7878"
        assert cfg.radarr.api_key == "testkey"
        assert cfg.radarr.is_configured is True

    def test_timeout_validation(self):
        cfg = ArrConfig(timeout="30")
        assert cfg.timeout == 30

    def test_load_with_os_env(self, monkeypatch):
        monkeypatch.setenv("SONARR_URL", "http://localhost:8989")
        monkeypatch.setenv("SONARR_API_KEY", "sonarr-key")
        monkeypatch.setenv("SONARR_ENABLED", "true")

        cfg = ArrConfig.load_config()
        assert cfg.sonarr.url == "http://localhost:8989"
        assert cfg.sonarr.api_key == "sonarr-key"
        assert cfg.sonarr.is_configured is True

    def test_mcp_transport_config(self):
        cfg = ArrConfig()
        assert cfg.transport.transport == "stdio"
        assert cfg.transport.host == "127.0.0.1"
        assert cfg.transport.port == 10938
        assert cfg.transport.path == "/mcp"
