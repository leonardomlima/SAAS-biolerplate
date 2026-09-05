from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"

        if request.url.path in ("/docs", "/redoc", "/openapi.json"):
            csp = "default-src 'self' 'unsafe-inline' 'unsafe-eval'; img-src 'self' data: https:; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; connect-src 'self' https://cdn.jsdelivr.net"
        else:
            csp = "default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self' 'unsafe-inline'"

        response.headers["Content-Security-Policy"] = csp
        return response
