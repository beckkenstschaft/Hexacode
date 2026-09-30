"""API v1 router."""

from fastapi import APIRouter

from app.api.v1 import health, sessions, benchmarks

router = APIRouter(prefix="/api/v1")

router.include_router(health.router)
router.include_router(sessions.router)
router.include_router(benchmarks.router)