"""Database engine and session factory.

Uses SQLAlchemy 2.x async mode with asyncpg.
"""

import time

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.config import settings


engine = create_async_engine(
    settings.database_url,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    connect_args={
        "timeout": 5,  # seconds — fail-fast instead of hanging 60 s (asyncpg default)
    },
)


async def probe_database_health() -> float:
    """Run a lightweight database probe and return its latency in milliseconds."""
    t0 = time.monotonic()
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return round((time.monotonic() - t0) * 1000, 2)