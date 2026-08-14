"""Prometheus metrics definitions and helper for FACCP platform services."""

from __future__ import annotations

from prometheus_client import Counter, Gauge, Histogram, make_asgi_app
from fastapi import FastAPI

HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["service", "method", "route", "status"],
)

HTTP_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration",
    ["service", "method", "route"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

EVENTS_PUBLISHED = Counter(
    "events_published_total",
    "Total published events",
    ["topic", "event_type"],
)

EVENTS_CONSUMED = Counter(
    "events_consumed_total",
    "Total consumed events",
    ["topic", "event_type", "consumer"],
)

EVENTS_FAILED = Counter(
    "events_failed_total",
    "Total failed events",
    ["topic", "event_type"],
)

EVENTS_DLQ = Counter(
    "events_dlq_total",
    "Total dead letter queue events",
    ["topic"],
)

SAGA_ACTIVE = Gauge(
    "saga_active_total",
    "Current active sagas by state",
    ["state"],
)


def setup_platform_metrics(app: FastAPI, service_name: str) -> None:
    """Mount Prometheus metrics endpoint on FastAPI app."""
    try:
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)
    except Exception:
        pass
