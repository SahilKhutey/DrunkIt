"""
SLO (Service Level Objective) tracking.
Provides:
- Latency histograms per operation
- Availability counters
- Error budget tracking
"""

from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Any

from prometheus_client import Counter, Gauge, Histogram

LATENCY_BUCKETS = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0)

order_processing_duration = Histogram(
    "order_processing_duration_seconds",
    "End-to-end order processing time",
    buckets=LATENCY_BUCKETS,
)
compliance_evaluation_duration = Histogram(
    "compliance_evaluation_duration_seconds",
    "Compliance evaluation time",
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)
payment_authorization_duration = Histogram(
    "payment_authorization_duration_seconds",
    "Payment authorization time",
    buckets=LATENCY_BUCKETS,
)

payment_events = Counter(
    "payment_events_total",
    "Payment events by type",
    ["event_type"],
)
compliance_decisions = Counter(
    "compliance_decisions_total",
    "Compliance decisions by outcome",
    ["decision"],
)
risk_evaluated = Counter(
    "risk_evaluated_v2_total",
    "Risk evaluations by level",
    ["level"],
)

audit_chain_total = Gauge("audit_chain_total", "Total audit events in chain")
audit_chain_verified = Gauge("audit_chain_verified", "Verified audit events")
audit_chain_broken_events = Gauge("audit_chain_broken_events", "Number of broken audit events")


@contextmanager
def track_latency(histogram: Histogram, **labels: Any):
    start = time.perf_counter()
    try:
        yield
    finally:
        duration = time.perf_counter() - start
        histogram.labels(**labels).observe(duration)


class ErrorBudget:

    def __init__(self, slo_name: str, target_availability: float, window_days: int = 30) -> None:
        self.slo_name = slo_name
        self.target = target_availability
        self.window_seconds = window_days * 86400
        self.total_requests = Counter(f"slo_{slo_name}_total", "Total requests")
        self.failed_requests = Counter(f"slo_{slo_name}_failed", "Failed requests")
        self.remaining_budget = Gauge(
            f"slo_{slo_name}_remaining_budget",
            "Remaining error budget (seconds of allowed downtime)",
        )

    def record_request(self, failed: bool) -> None:
        self.total_requests.inc()
        if failed:
            self.failed_requests.inc()
        total = getattr(self.total_requests, "_value", {}).get((), 0)
        failed_count = getattr(self.failed_requests, "_value", {}).get((), 0)
        if total > 0:
            observed_availability = 1.0 - (failed_count / total)
            remaining = max(0.0, (self.target - observed_availability)) * self.window_seconds
            self.remaining_budget.set(remaining)
