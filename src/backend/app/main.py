"""Backend API — FastAPI application factory.

Creates and configures the ASGI application with:
- Structured JSON logging
- CORS middleware
- API router registration
- Standardized error handlers
- Startup/shutdown lifecycle hooks
"""

import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.router import router as api_router
from app.config import settings
from app.core.database import check_database_connection
from app.logging import configure_logging, get_logger
from app.version import APP_VERSION

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — configure logging, verify database connectivity,
    cleanup on shutdown.

    Fails fast if the database is unreachable or if required secrets are missing.
    """
    configure_logging()

    await check_database_connection()

    logger.info("Backend starting")
    yield
    logger.info("Backend stopping")


def create_app() -> FastAPI:
    """Build and return the configured FastAPI application."""
    app = FastAPI(
        title="Backend API",
        version=APP_VERSION,
        docs_url=settings.docs_url,
        redoc_url=settings.redoc_url,
        openapi_url=settings.openapi_url,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin.split(","),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Accept-Language", "X-Request-ID"],
    )

    # ── Correlation ID middleware ─────────────────────────────────────
    @app.middleware("http")
    async def correlation_id_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", uuid.uuid4().hex[:16])
        # Bind to structlog context so every log entry carries the request ID.
        import structlog.contextvars
        structlog.contextvars.bind_contextvars(request_id=request_id)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

    # ── Global error handler ──────────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception(
            "Unhandled exception",
            path=request.url.path,
            method=request.method,
        )
        return JSONResponse(
            status_code=500,
            content={"error": {"code": "INTERNAL_ERROR", "message": "An internal error occurred"}},
        )

    # API routes
    app.include_router(api_router)

    return app


app = create_app()
