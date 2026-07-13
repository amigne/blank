"""API v1 top-level router — aggregates all v1 resource routers."""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")
