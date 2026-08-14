"""Distributed tracing setup for platform services."""

from __future__ import annotations

import uuid
from typing import Any


def get_trace_id() -> str:
    """Extract current OpenTelemetry trace ID or generate fallback UUID hex string."""
    try:
        from opentelemetry import trace
        span = trace.get_current_span()
        context = span.get_span_context()
        if context and context.trace_id:
            return format(context.trace_id, "032x")
    except Exception:
        pass
    return uuid.uuid4().hex


def configure_tracing(service_name: str, endpoint: str | None = None) -> None:
    """Initialize OpenTelemetry TracerProvider and optional OTLP exporter."""
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)

        if endpoint:
            try:
                from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
                exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
                provider.add_span_processor(BatchSpanProcessor(exporter))
            except Exception:
                pass

        trace.set_tracer_provider(provider)
    except Exception:
        pass


def setup_platform_tracing(service_name: str, environment: str = "development") -> None:
    """Legacy alias initializing OpenTelemetry tracer provider."""
    configure_tracing(service_name)
