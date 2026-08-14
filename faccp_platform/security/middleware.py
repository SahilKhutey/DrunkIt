"""Security headers and request size limit middleware."""

from __future__ import annotations

from typing import Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse

MAX_BODY_SIZE = 10 * 1024 * 1024  # 10MB limit


async def security_headers_middleware(request: Request, call_next: Any) -> Response:
    """Middleware attaching standard HTTP security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=()"
    return response


async def request_size_limit_middleware(request: Request, call_next: Any) -> Response:
    """Middleware enforcing maximum HTTP request body size."""
    content_length = request.headers.get("content-length")
    if content_length:
        try:
            if int(content_length) > MAX_BODY_SIZE:
                return JSONResponse(
                    status_code=413,
                    content={"detail": "Request payload exceeds maximum allowed size (10MB)"},
                )
        except ValueError:
            pass
    return await call_next(request)
