"""Health-check endpoints.

- ``GET /health`` — public, lightweight liveness/readiness.
- ``GET /health/full`` — protected, dependency status (requires X-Health-Token header).
"""

import secrets
import time

from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Annotated, Literal

from app.config import settings
from app.core.database import probe_database_health
from app.version import APP_VERSION

# ── Response models ──────────────────────────────────────────────────


class HealthPublicResponse(BaseModel):
    status: Literal["ok"]


class DependencyStatus(BaseModel):
    status: Literal["ok", "unavailable"]
    latency_ms: float | None


class HealthFullResponse(BaseModel):
    status: Literal["ok", "degraded"]
    version: str
    build_number: str
    uptime_seconds: float
    dependencies: dict[str, DependencyStatus]


# ── Router ───────────────────────────────────────────────────────────

_started_at = time.time()

router = APIRouter(tags=["health"])


def _forbidden_health_response() -> JSONResponse:
    """Return the uniform forbidden envelope for protected health access."""
    return JSONResponse(
        status_code=403,
        content={
            "error": {
                "code": "API_FORBIDDEN",
                "details": [],
            },
        },
    )


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


@router.get("/health", response_model=HealthPublicResponse)
async def health_public():
    """Public health check — liveness and readiness only.

    Returns lightweight status. Does not expose dependency details.
    """
    return {
        "status": "ok",
    }


@router.get("/health/full", response_model=HealthFullResponse)
async def health_full(
    x_health_token: Annotated[str | None, Header(alias="X-Health-Token")] = None,
):
    """Protected full health check — includes dependency status.

    Requires ``X-Health-Token`` header matching the ``HEALTH_FULL_TOKEN`` deployment secret.
    Missing and invalid tokens both receive a generic 403 Forbidden response.
    Token comparison uses constant-time ``secrets.compare_digest``.
    """
    if not _health_token_matches(x_health_token):
        return _forbidden_health_response()

    db_status = "ok"
    db_latency_ms: float | None = None

    try:
        db_latency_ms = await probe_database_health()
    except Exception:
        db_status = "unavailable"
        db_latency_ms = None

    overall = "ok" if db_status == "ok" else "degraded"
    
    return {
        "status": overall,
        "version": APP_VERSION,
        "build_number": settings.build_number,
        "uptime_seconds": round(time.time() - _started_at, 3),
        "dependencies": {
            "database": {
                "status": db_status,
                "latency_ms": db_latency_ms,
            },
        },
    }