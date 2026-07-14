"""Regression tests for the structured logging baseline."""

import json
import structlog

from app.config import settings
from app.logging import configure_logging, get_logger


def test_configure_logging_emits_json_to_stdout(capsys, monkeypatch):
    """The logging baseline must stay JSON even when tests run with a TTY-like stdout."""
    structlog.reset_defaults()

    # Decouple from the ambient LOG_LEVEL: this test emits an INFO probe, so it
    # must configure logging at INFO regardless of the scenario's log level
    # (e.g. the test container runs with LOG_LEVEL=WARNING, which would filter it).
    monkeypatch.setattr(settings, "log_level", "INFO")

    configure_logging()
    get_logger("test").info("probe", component="test")

    captured = capsys.readouterr()
    payload = json.loads(captured.out.strip())

    assert captured.err == ""
    assert payload["event"] == "probe"
    assert payload["component"] == "test"
    assert payload["level"] == "info"
    assert "timestamp" in payload