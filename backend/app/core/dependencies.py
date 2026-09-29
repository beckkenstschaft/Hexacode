"""FastAPI dependencies."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings, Settings
from app.core.logging import get_logger
from app.db.session import get_session_factory

logger = get_logger(__name__)


def get_settings_dep() -> Settings:
    """Get application settings."""
    return get_settings()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_request_id(request: Request) -> str:
    """Get or generate request ID."""
    return request.headers.get("X-Request-ID", request.state.request_id if hasattr(request.state, "request_id") else "")


async def verify_content_length(
    request: Request,
    settings: Settings = Depends(get_settings_dep),
) -> None:
    """Verify request content length."""
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"Request too large. Max size: {settings.MAX_UPLOAD_SIZE} bytes",
        )


@asynccontextmanager
async def lifespan(app: "FastAPI") -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info("application_starting")
    settings = get_settings()
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("application_started", environment=settings.ENVIRONMENT)
    yield
    # Shutdown
    logger.info("application_shutting_down")