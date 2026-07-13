"""Health-check endpoints.

- ``GET /health`` — public, lightweight liveness/readiness.
- ``GET /health/full`` — protected, dependency status (requires X-Health-Token header).
"""

import secrets
import time

from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse
from typing import Annotated

from app.config import settings

_started_at = time.time()

router = APIRouter(tags=["health"])


_FORBIDDEN_HEALTH_RESPONSE = {
    "error": {
        "code": "API_FORBIDDEN",
        "details": [],
    },
}


def _forbidden_health_response() -> JSONResponse:
    """Return the uniform forbidden envelope for protected health access."""
    return JSONResponse(status_code=403, content=_FORBIDDEN_HEALTH_RESPONSE)


def _health_token_matches(x_health_token: str | None) -> bool:
    """Return True only when the provided header matches the configured token."""
    if x_health_token is None:
        return False

    # Time safe comparison to avoid leaking information about the token via timing attacks.
    has_health_token_configured = settings.health_full_token is not None

    alternative_token = secrets.token_hex(32)

    comparison_result = secrets.compare_digest(
        x_health_token.encode("utf-8"),
        settings.health_full_token.get_secret_value().encode("utf-8")
        if has_health_token_configured
        else alternative_token.encode("utf-8"),
    )

    return has_health_token_configured and comparison_result


@router.get("/health")
async def health_public() -> dict[str, object]:
    """Public health check — liveness and readiness only.

    Returns lightweight status. Does not expose dependency details.
    """
    return {
        "status": "ok",
    }


@router.get("/health/full")
async def health_full(
    x_health_token: Annotated[str | None, Header(alias="X-Health-Token")] = None,
) -> dict[str, object]:
    """Protected full health check — includes dependency status.

    Requires ``X-Health-Token`` header matching the ``HEALTH_FULL_TOKEN`` deployment secret.
    Missing and invalid tokens both receive a generic 403 Forbidden response.
    Token comparison uses constant-time ``secrets.compare_digest``.
    """
    if not _health_token_matches(x_health_token):
        return _forbidden_health_response()

    overall = "ok"  # TODO: remove when we implement dependency checks

    return {
        "status": overall,
        "version": "0.1.0",  # TODO: auto-insert from package version
        "uptime_seconds": round(time.time() - _started_at, 3),
        "dependencies": {},
    }
