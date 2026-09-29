"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import api_v1_router
from app.core.config import get_settings
from app.core.dependencies import lifespan
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.db.session import close_db

logger = get_logger(__name__)


@asynccontextmanager
async def app_lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    configure_logging()
    settings = get_settings()
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("application_starting", environment=settings.ENVIRONMENT)
    yield
    # Shutdown
    logger.info("application_shutting_down")
    await close_db()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.PRODUCT_NAME,
        description="Offline NPU-first meeting and classroom copilot",
        version="0.1.0",
        lifespan=app_lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    register_exception_handlers(app)

    # Routes
    app.include_router(api_v1_router)

    @app.get("/")
    async def root():
        return {
            "product": settings.PRODUCT_NAME,
            "version": "0.1.0",
            "docs": "/docs",
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=settings.WORKERS,
    )