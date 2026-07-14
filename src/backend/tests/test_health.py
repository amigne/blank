"""Tests for health-check endpoints and config security.

Covers:
- Public /health returns 200 with expected keys.
- Protected /health/full returns 403 without token.
- Protected /health/full returns 403 with wrong token.
- Protected /health/full returns 200 with correct token.
- Settings.check_secrets() rejects placeholder values.
- Settings.check_secrets() enforces SMTP and backup secrets in production/test.
- API lifespan verifies database connectivity at startup.
"""

import pytest

from httpx import Request

class TestPublicHealth:
    """Public health endpoint tests."""

    async def test_health_returns_ok(self, client):
        """GET /health should return 200 with status=ok."""
        response = await client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"

    async def test_health_does_not_expose_infrastructure_info(self, client):
        """Public health must NOT expose infrastructure information)."""
        response = await client.get("/health")
        body = response.json()
        assert "version" not in body
        assert "build_number" not in body
        assert "uptime_seconds" not in body
        assert "dependencies" not in body


class TestProtectedHealth:
    """Protected full health endpoint tests (INFRA-013)."""

    @staticmethod
    def assert_forbidden_envelope(response) -> None:
        """Assert the uniform forbidden response shape."""
        assert response.status_code == 403
        assert response.json() == {
            "error": {
                "code": "API_FORBIDDEN",
                "details": [],
            },
        }

    async def test_full_health_requires_token(self, client):
        """GET /health/full without X-Health-Token must return 403
        (the header is now optional at the FastAPI boundary; the handler
        returns a generic forbidden response for both missing and wrong tokens).
        """
        response = await client.get("/health/full")
        self.assert_forbidden_envelope(response)

    async def test_full_health_rejects_wrong_ascii_token(self, client):
        """GET /health/full with wrong token must return 403."""
        response = await client.get(
            "/health/full",
            headers={"X-Health-Token": "wrong-token"},
        )
        self.assert_forbidden_envelope(response)

    async def test_full_health_rejects_non_ascii_token(self, client):
        """Non-ASCII token input must still be treated as a generic 403."""
        request = Request(
            "GET",
            "http://test/health/full",
            headers=[(b"X-Health-Token", b"caf\xe9")],
        )
        response = await client.send(request)
        self.assert_forbidden_envelope(response)

    async def test_full_health_accepts_correct_token_mocked_db(self, client, monkeypatch):
        """GET /health/full with correct token returns 200 when DB is mocked."""
        from app import config
        from pydantic import SecretStr

        monkeypatch.setattr(
            config.settings, "health_full_token", SecretStr("test-health-token")
        )

        response = await client.get(
            "/health/full",
            headers={"X-Health-Token": "test-health-token"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert "version" in body
        assert "build_number" in body
        assert "uptime_seconds" in body
        assert isinstance(body["uptime_seconds"], (int, float))
        assert "dependencies" in body
        assert isinstance(body["dependencies"], dict)
        assert "database" in body["dependencies"]
        assert isinstance(body["dependencies"]["database"], dict)
        assert "status" in body["dependencies"]["database"]
        assert "latency_ms" in body["dependencies"]["database"]
        assert isinstance(body["dependencies"]["database"]["latency_ms"], (int, float))