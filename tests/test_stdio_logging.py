"""Regression coverage for stdio-safe server logging."""

from __future__ import annotations

import logging

from rich.logging import RichHandler

from arr_mcp.server import setup_logging


def test_setup_logging_routes_rich_logs_to_stderr_without_stdout(capsys):
    root = logging.getLogger()
    original_handlers = root.handlers[:]
    original_level = root.level
    watched_loggers = {
        name: logging.getLogger(name).level for name in ("httpx", "httpcore", "uvicorn")
    }

    try:
        root.handlers.clear()
        setup_logging("INFO")

        rich_handlers = [handler for handler in root.handlers if isinstance(handler, RichHandler)]
        assert len(rich_handlers) == 1
        assert rich_handlers[0].console.stderr is True

        logging.getLogger("stdio-regression").info("stdio-safe log")
        captured = capsys.readouterr()
        assert "stdio-safe log" not in captured.out
        assert "stdio-safe log" in captured.err
    finally:
        for handler in root.handlers:
            handler.close()
        root.handlers[:] = original_handlers
        root.setLevel(original_level)
        for name, level in watched_loggers.items():
            logging.getLogger(name).setLevel(level)
