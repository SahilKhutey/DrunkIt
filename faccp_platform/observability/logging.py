"""Structured logging setup for platform services."""

from __future__ import annotations

import logging
import sys
from typing import Any
import structlog


def configure_logging(
    service_name: str = "faccp-service",
    log_level: str = "INFO",
) -> None:
    """Configure structlog and standard logging with ISO timestamps and JSON output."""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper(), logging.INFO),
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def setup_platform_logging(
    service_name: str = "faccp-service",
    log_level: str = "INFO",
) -> None:
    """Legacy alias for platform logging setup."""
    configure_logging(service_name=service_name, log_level=log_level)
