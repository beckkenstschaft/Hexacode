"""Health check endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.dependencies import get_db
from app.core.logging import get_logger
from app.schemas.api import HealthResponse

router = APIRouter(tags=["health"])
logger = get_logger(__name__)


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Basic health check."""
    return HealthResponse(status="healthy", timestamp=datetime.now())


@router.get("/ready", response_model=HealthResponse)
async def readiness_check(session: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Readiness check including database connectivity."""
    try:
        await session.execute(text("SELECT 1"))
        return HealthResponse(status="ready", timestamp=datetime.now())
    except Exception as e:
        logger.error("readiness_check_failed", error=str(e))
        return HealthResponse(status="not_ready", timestamp=datetime.now())


@router.get("/system/capabilities")
async def system_capabilities() -> dict:
    """Get system capabilities and available providers."""
    from app.engines.factory import get_engine_factory
    from app.engines.provider_selector import get_provider_selector

    settings = get_settings()
    selector = get_provider_selector()
    factory = get_engine_factory()

    capabilities = selector.get_capabilities()

    # Check which models are loaded
    vad = factory.get_vad()
    asr = factory.get_asr()
    summarizer = factory.get_summarizer()

    return {
        "product_name": settings.PRODUCT_NAME,
        "providers": capabilities,
        "models_loaded": {
            "vad": {"provider": vad.provider, "simulated": vad.simulated},
            "asr": {"provider": asr.provider, "simulated": asr.simulated},
            "summarizer": {"provider": summarizer.provider, "simulated": summarizer.simulated},
        },
        "simulated_mode": settings.USE_MOCK_ENGINES,
    }