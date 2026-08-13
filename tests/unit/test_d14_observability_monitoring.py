"""
Master unit test for Phase D14 Observability, Monitoring & Reliability Engine.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from services.observability.app.engine.alert_engine import AlertEngine
from services.observability.app.engine.health_engine import HealthEngine
from services.observability.app.engine.slo_engine import SLOEngine
from services.observability.app.middleware.request_logging import StructuredLogger, redact
from services.observability.app.middleware.request_metrics import RequestMetrics
from services.observability.app.services.alert_service import AlertService
from services.observability.app.services.health_service import HealthService
from services.observability.app.services.incident_service import IncidentService
from services.observability.app.services.metrics_service import MetricsService
from services.observability.app.services.trace_service import TraceService


@pytest.mark.asyncio
async def test_full_d14_observability_monitoring_pipeline():
    # 1. Health Engine Evaluation
    health_engine = HealthEngine()
    health_res = await health_engine.evaluate()
    assert health_res["status"] == "healthy"
    assert health_res["checks"]["database"] is True

    # 2. Structured Logging & Sensitivity Redaction
    logger = StructuredLogger("order-service")
    log_record = logger.info("payment.processed", payment_id="pay_001", card_number="1234-5678-9012-3456", password="secret_pass")
    assert log_record["card_number"] == "[REDACTED]"
    assert log_record["password"] == "[REDACTED]"
    assert log_record["payment_id"] == "pay_001"

    # 3. Request Metrics Recording
    metrics = RequestMetrics()
    metrics.record(0.120, error=False)
    metrics.record(0.180, error=False)
    metrics.record(0.300, error=True)

    assert metrics.requests == 3
    assert metrics.errors == 1
    assert round(metrics.average_latency, 2) == 0.20
    assert round(metrics.error_rate, 2) == 0.33

    # 4. Alert Engine & SHA-256 Deduplication
    alert_svc = AlertService()
    a1 = await alert_svc.create_alert("PAYMENT_LATENCY_HIGH", "payment-service", "CRITICAL", "P95 > 200ms")
    a2 = await alert_svc.create_alert("PAYMENT_LATENCY_HIGH", "payment-service", "CRITICAL", "P95 > 200ms")

    assert a1["fingerprint"] == a2["fingerprint"]
    assert a2["count"] == 2

    # 5. Incident Engine & Lifecycle Workflow
    inc_svc = IncidentService()
    inc = await inc_svc.create_incident("payment-service", "High payment latency", "CRITICAL")
    assert inc["status"] == "OPEN"
    assert inc["incident_code"].startswith("INC-")

    ack = await inc_svc.acknowledge_incident(inc["id"], "ops-lead-surat")
    assert ack["status"] == "ACKNOWLEDGED"

    res = await inc_svc.resolve_incident(inc["id"])
    assert res["status"] == "RESOLVED"

    # 6. SLO Engine Availability & Error Budget
    slo_engine = SLOEngine()
    avail = slo_engine.calculate_availability(999500, 1000000)
    eb = slo_engine.calculate_error_budget(1000000, 99.95)

    assert avail == 99.95
    assert round(eb) == 500

    # 7. Distributed Tracing Spans
    trace_svc = TraceService()
    span = trace_svc.start_span("trace_001", "create_order", "order-service")
    trace_svc.finish_span(span["span_id"], 45.0, "OK")
    assert span["duration_ms"] == 45.0
