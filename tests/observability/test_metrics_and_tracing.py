"""Integration tests for observability, metrics middleware, health probes, and distributed tracing."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from faccp_platform.health.checks import health_router
from faccp_platform.observability.middleware import metrics_middleware
from faccp_platform.observability.tracing import get_trace_id


def test_metrics_and_health_endpoints():
    """Verify /health/live, /health/ready, and /metrics endpoints on FastAPI service."""
    app = FastAPI(title="test-service")
    app.middleware("http")(metrics_middleware)
    app.include_router(health_router)

    client = TestClient(app)

    # 1. Test /health/live
    res_live = client.get("/health/live")
    assert res_live.status_code == 200
    assert res_live.json() == {"status": "ok"}

    # 2. Test /health/ready
    res_ready = client.get("/health/ready")
    assert res_ready.status_code == 200
    assert res_ready.json() == {"status": "ready"}

    # 3. Test /metrics
    res_metrics = client.get("/metrics")
    assert res_metrics.status_code == 200
    assert "http_requests_total" in res_metrics.text


def test_get_trace_id():
    """Verify trace ID generation produces a 32-char hex string."""
    tid = get_trace_id()
    assert isinstance(tid, str)
    assert len(tid) == 32
