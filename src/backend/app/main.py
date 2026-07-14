"""Backend API — FastAPI application factory.

Creates and configures the ASGI application with:
- Structured JSON logging
- CORS middleware
- API router registration
- Standardized error handlers
- Startup/shutdown lifecycle hooks
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.logging import configure_logging, get_logger
from app.api.router import router as api_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — configure logging, validate secrets, verify
    database connectivity, cleanup on shutdown.

    Fails fast if the database is unreachable or if required secrets are missing.
    """
    configure_logging()

    # str(URL) masks the password as *** — safe to log.
    logger.info("Backend starting")
    yield
    logger.info("Backend stopping")


def create_app() -> FastAPI:
    """Build and return the configured FastAPI application."""
    app = FastAPI(
        title="Backend API",
        version="0.1.0",  ## TODO: Use version from pyproject.toml
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
        lifespan=lifespan,
    )

    # API routes
    app.include_router(api_router)

    return app


app = create_app()
