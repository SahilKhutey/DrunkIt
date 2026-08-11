from __future__ import annotations

import logging
import sys
from typing import Any

try:
    import structlog
    from structlog.types import EventDict, Processor
except ModuleNotFoundError:  # pragma: no cover - fallback for minimal test envs
    structlog = None  # type: ignore[assignment]
    EventDict = dict[str, Any]  # type: ignore[misc, assignment]
    Processor = Any  # type: ignore[misc, assignment]


def _add_service_info(service_name: str, service_version: str) -> Processor:
    def processor(_: Any, __: EventDict) -> EventDict:
        return {"service": service_name, "service_version": service_version}
    return processor


def configure_logging(
    service_name: str,
    service_version: str,
    level: str = "INFO",
    environment: str = "local",
    json_output: bool | None = None,
) -> None:
    """Configure structured logging for a service."""
    if structlog is None:
        logging.basicConfig(
            format="%(asctime)s %(levelname)s %(name)s %(message)s",
            stream=sys.stdout,
            level=getattr(logging, level.upper(), logging.INFO),
        )
        return

    if json_output is None:
        json_output = environment in ("production", "staging")

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper(), logging.INFO),
    )

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        _add_service_info(service_name, service_version),
    ]

    if json_output:
        processors: list[Processor] = [
            *shared_processors,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
    else:
        processors = [
            *shared_processors,
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> Any:
    """Get a structured logger."""
    if structlog is None:
        return logging.getLogger(name)
    return structlog.get_logger(name)
