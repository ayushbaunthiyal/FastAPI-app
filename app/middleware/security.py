"""Security headers middleware."""
from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    def __init__(self, app: Callable[[dict, Callable, Callable], Awaitable[Response]]) -> None:
        super().__init__(app)
        from app.core.config import settings
        self.settings = settings

    async def dispatch(
        self, request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Force HTTPS redirect
        if self.settings.HTTPS_REDIRECT and request.url.scheme != "https":
            from starlette.responses import RedirectResponse
            url = request.url.replace(scheme="https")
            return RedirectResponse(url=str(url), status_code=307)

        response = await call_next(request)

        # HSTS (Strict-Transport-Security)
        if self.settings.HTTPS_REDIRECT:
            preload = "; preload" if self.settings.HSTS_PRELOAD else ""
            include_subdomains = "; includeSubDomains" if self.settings.HSTS_INCLUDE_SUBDOMAINS else ""
            response.headers["Strict-Transport-Security"] = (
                f"max-age={self.settings.HSTS_SECONDS}{include_subdomains}{preload}"
            )

        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # XSS protection
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions policy
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Content Security Policy (Basic default)
        # response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"

        return response
