"""Database engine and session factory.

Uses SQLAlchemy 2.x async mode with asyncpg.
"""

import time

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.config import settings

_engine: AsyncEngine | None = None


def get_engine() -> AsyncEngine:
    """Return the async engine, creating it lazily on first call.

    The engine is not created at module import time — this avoids
    side effects when importing the module (e.g. in tests or scripts)
    and gives a clear error at startup if database settings are invalid.
    """
    global _engine
    if _engine is None:
        _engine = create_async_engine(
            settings.database_url,
            echo=False,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            connect_args={
                "timeout": 5,  # seconds — fail-fast instead of hanging 60 s (asyncpg default)
            },
        )
    return _engine


async def probe_database_health() -> float:
    """Run a lightweight database probe and return its latency in milliseconds."""
    t0 = time.monotonic()
    async with get_engine().connect() as conn:
        await conn.execute(text("SELECT 1"))
    return round((time.monotonic() - t0) * 1000, 2)

async def check_database_connection() -> None:
    """Verify database connectivity at startup.

    Raises an exception if the database is unreachable, causing the
    application container to fail early rather than starting with a
    degraded state. Docker Compose restart policy handles retries.
    """
    await probe_database_health()