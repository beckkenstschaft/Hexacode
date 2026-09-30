"""Custom exceptions and error handling."""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.logging import get_logger

logger = get_logger(__name__)


class AppError(Exception):
    """Base application error."""

    def __init__(
        self,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    """Resource not found error."""

    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(
            code="NOT_FOUND",
            message=f"{resource} not found",
            details={"resource": resource, "identifier": identifier},
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ValidationError(AppError):
    """Input validation error."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            details=details or {},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class EngineError(AppError):
    """ML engine error."""

    def __init__(self, stage: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            code="ENGINE_ERROR",
            message=f"{stage}: {message}",
            details={"stage": stage, **(details or {})},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class ProviderUnavailableError(AppError):
    """Execution provider not available error."""

    def __init__(self, provider: str, stage: str) -> None:
        super().__init__(
            code="PROVIDER_UNAVAILABLE",
            message=f"Provider {provider} not available for {stage}",
            details={"provider": provider, "stage": stage},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


def create_error_response(
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
) -> JSONResponse:
    """Create standardized error response."""
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            }
        },
    )


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Handle application errors."""
    logger.warning(
        "app_error",
        code=exc.code,
        message=exc.message,
        details=exc.details,
        path=request.url.path,
    )
    return create_error_response(exc.code, exc.message, exc.details, exc.status_code)


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    details = {"errors": exc.errors()}
    logger.warning("validation_error", details=details, path=request.url.path)
    return create_error_response("VALIDATION_ERROR", "Invalid input", details, status.HTTP_422_UNPROCESSABLE_ENTITY)


async def generic_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected errors."""
    logger.exception("unhandled_error", path=request.url.path, error=str(exc))
    return create_error_response(
        "INTERNAL_ERROR",
        "An unexpected error occurred",
        {"type": type(exc).__name__},
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers."""
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(Exception, generic_error_handler)