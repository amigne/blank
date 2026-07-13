"""Regression tests for the structured logging baseline."""

import json
import structlog

from app.logging import configure_logging, get_logger


def test_configure_logging_emits_json_to_stdout(capsys):
    """The logging baseline must stay JSON even when tests run with a TTY-like stdout."""
    structlog.reset_defaults()

    configure_logging()
    get_logger("test").info("probe", component="test")

    captured = capsys.readouterr()
    payload = json.loads(captured.out.strip())

    assert captured.err == ""
    assert payload["event"] == "probe"
    assert payload["component"] == "test"
    assert payload["level"] == "info"
    assert "timestamp" in payload