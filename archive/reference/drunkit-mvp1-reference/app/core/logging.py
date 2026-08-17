"""
Structured logging.

- JSON output in production (machine-parseable, ships to any log
  aggregator), pretty console output in development.
- Every log line inside a request is automatically tagged with that
  request's correlation ID via RequestIdMiddleware + structlog's
  contextvars binding — no need to thread a request_id parameter
  through every function call by hand.
- Deliberately never logs: OTP codes, session tokens/bearer values,
  raw phone numbers (masked instead), dates of birth. See mask_phone()
  and the call sites in domain/auth and domain/eligibility.
"""
from __future__ import annotations

import logging
import sys
import uuid

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.config import get_settings

settings = get_settings()


def configure_logging() -> None:
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.environment == "production":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer()

    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = "drunkit"):
    return structlog.get_logger(name)


def mask_phone(phone: str) -> str:
    """9123456789 -> ***6789. Enough to correlate log lines to a
    support ticket without a bare phone number sitting in log storage."""
    if len(phone) <= 4:
        return "*" * len(phone)
    return "*" * (len(phone) - 4) + phone[-4:]


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Assigns a correlation ID to every request (or reuses one supplied
    via X-Request-ID, so an upstream gateway's ID threads through),
    binds it into structlog's contextvars for the duration of the
    request, and echoes it back in the response header so a client
    can quote it when reporting an issue.
    """

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
