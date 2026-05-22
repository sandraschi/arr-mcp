"""Tests for transport CLI flag parsing."""

import sys

from arr_mcp.transport import parse_argv_flags, resolve_transport_from_argv


class TestTransportArgv:
    def test_default_stdio(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["arr-mcp"])
        transport, port = parse_argv_flags()
        assert transport == "stdio"
        assert port is None

    def test_http_flag(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["arr-mcp", "--http"])
        transport, port = parse_argv_flags()
        assert transport == "http"
        assert port is None

    def test_http_with_port(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["arr-mcp", "--http", "--port", "10938"])
        transport, port = parse_argv_flags()
        assert transport == "http"
        assert port == 10938

    def test_sse_flag(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["arr-mcp", "--sse", "--port", "8080"])
        transport, port = parse_argv_flags()
        assert transport == "sse"
        assert port == 8080

    def test_resolve_transport_legacy(self, monkeypatch):
        monkeypatch.setattr(sys, "argv", ["arr-mcp", "--sse"])
        assert resolve_transport_from_argv() == "sse"
