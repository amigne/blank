"""Tests for API lifespan.

Covers:
- API lifespan verifies database connectivity at startup.
"""

from unittest.mock import AsyncMock, patch


class TestAPILifespan:
    """Tests for the API lifespan — database startup probe."""

    async def test_lifespan_calls_database_check(self):
        """The API lifespan must verify database connectivity at startup."""
        with(
            patch("app.main.check_database_connection", new_callable=AsyncMock) as mock_check
        ):
            from app.main import lifespan

            async with lifespan(None):
                pass
            
            mock_check.assert_awaited_once()