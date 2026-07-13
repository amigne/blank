"""Shared test fixtures for the backend test suite.

Uses httpx.AsyncClient to exercise the FastAPI application without network.
"""

import os

import pytest

from httpx import ASGITransport, AsyncClient
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

# ── Application fixture ───────────────────────────────────────────────────────


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    """Yield an httpx AsyncClient wired to the FastAPI app via ASGI transport.

    Uses the module-level app singleton from ``app.main`` so that
    ``dependency_overrides`` set in tests take effect.
    """
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac