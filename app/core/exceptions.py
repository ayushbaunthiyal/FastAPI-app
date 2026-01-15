"""Custom exception classes and handlers."""
import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppException(Exception):
    """Base exception for application errors."""

    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "APP_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(AppException):
    """Resource not found."""

    def __init__(self, resource: str, resource_id: Any = None) -> None:
        message = f"{resource} not found"
        if resource_id:
            message = f"{resource} with id '{resource_id}' not found"
        super().__init__(message=message, status_code=404, error_code="NOT_FOUND")


class ValidationError(AppException):
    """Validation error."""

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details or {},
        )


class AuthenticationError(AppException):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(message=message, status_code=401, error_code="AUTHENTICATION_ERROR")


class AuthorizationError(AppException):
    """Authorization failed."""

    def __init__(self, message: str = "Permission denied") -> None:
        super().__init__(message=message, status_code=403, error_code="AUTHORIZATION_ERROR")


class ConflictError(AppException):
    """Resource conflict (e.g., duplicate)."""

    def __init__(self, message: str) -> None:
        super().__init__(message=message, status_code=409, error_code="CONFLICT")


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "-")
        logger.warning(
            f"AppException: {exc.message}",
            extra={"request_id": request_id, "error_code": exc.error_code},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.error_code,
                "message": exc.message,
                "details": exc.details,
                "request_id": request_id,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "-")
        logger.exception(
            f"Unhandled exception: {exc}",
            extra={"request_id": request_id},
        )
        # Hide internal error details in production
        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "request_id": request_id,
            },
        )
