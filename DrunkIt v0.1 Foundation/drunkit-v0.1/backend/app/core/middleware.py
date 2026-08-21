"""Request context management and middleware for correlation IDs and performance tracing."""

import contextvars
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Context variable storing the active request's correlation ID
request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="")


def get_current_request_id() -> str:
    """Retrieve the correlation ID of the currently executing request context."""
    req_id = request_id_ctx.get()
    if not req_id:
        req_id = str(uuid.uuid4())
        request_id_ctx.set(req_id)
    return req_id


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware extracting or generating X-Request-ID and recording latency."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        # Extract existing request ID or generate a new UUIDv4
        incoming_request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_ctx.set(incoming_request_id)
        request.state.request_id = incoming_request_id

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            request_id_ctx.reset(token)

        response.headers["X-Request-ID"] = incoming_request_id
        response.headers["X-Response-Time-MS"] = f"{duration_ms:.2f}"
        return response


def register_middleware(app: FastAPI) -> None:
    """Register core platform middleware on the FastAPI application instance."""
    app.add_middleware(RequestContextMiddleware)
