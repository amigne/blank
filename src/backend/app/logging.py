"""Structured JSON logging configuration.

Uses structlog to emit JSON lines to stdout.
"""

import logging
import structlog
import sys

from app.config import settings


def configure_logging() -> None:
    """Configure structured logging for JSON-formatted stdout logging.

    Uses the log level from settings. All loggers emit to stdout in JSON format.
    Third-party loggers are routed through the same processor chain.
    """
    level = getattr(logging, settings.log_level)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Route stdlib logging through structlog
    logging.basicConfig(
        format="%(message)s", stream=sys.stdout, level=level, force=True
    )

    # Silence noisy third-party loggers at INFO
    for name in ("uvicorn.access", "uvicorn.error", "apscheduler"):
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """Return a bound structlog logger for the given name."""
    return structlog.get_logger(name or __name__)
