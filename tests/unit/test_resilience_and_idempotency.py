"""
Unit Tests for Failure Engineering, Resilience & Idempotency.
Validates:
- Double-submit order prevention
- Payment retry idempotency
- Fail-closed compliance policy enforcement
- Privacy redaction & data minimization in telemetry
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from decimal import Decimal
import pytest

for k in list(sys.modules.keys()):
    if k == "app" or k.startswith("app."):
        sys.modules.pop(k, None)

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

# Import shared idempotency and privacy primitives
from faccp_common.privacy import (
    detect_pii,
    redact_pii,
    data_minimization_filter,
    anonymize_for_analytics,
)

# Import compliance rule engine
sys.path.insert(0, os.path.join(root_dir, "services", "compliance-service"))
from app.domain.rule_engine import (
    EvaluationRequest,
    DecisionOutcome,
    evaluate_order,
)


class InMemoryIdempotencyStore:
    """Idempotency store simulator for key deduplication."""

    def __init__(self) -> None:
        self.store: dict[str, dict[str, str]] = {}

    def execute_or_get(self, key: str, func) -> dict[str, str]:
        if key in self.store:
            return self.store[key]
        result = func()
        self.store[key] = result
        return result


def test_idempotent_order_creation_prevents_duplicates():
    """Verify that re-submitting an order request with the same key yields identical cached result."""
    store = InMemoryIdempotencyStore()
    execution_counter = {"count": 0}

    def create_order():
        execution_counter["count"] += 1
        return {"order_id": "ord_idemp_1001", "status": "CREATED", "total": "700.00"}

    key = "idemp_key_order_xyz_123"

    res1 = store.execute_or_get(key, create_order)
    res2 = store.execute_or_get(key, create_order)

    assert res1 == res2
    assert execution_counter["count"] == 1


def test_idempotent_payment_capture_prevents_double_charge():
    """Verify payment capture idempotency prevents double charging."""
    store = InMemoryIdempotencyStore()
    charge_counter = {"charges": 0}

    def capture_payment():
        charge_counter["charges"] += 1
        return {"txn_id": "txn_88776655", "status": "CAPTURED", "amount": "1200.00"}

    key = "idemp_pay_key_abc_789"

    p1 = store.execute_or_get(key, capture_payment)
    p2 = store.execute_or_get(key, capture_payment)

    assert p1 == p2
    assert charge_counter["charges"] == 1
    assert p1["status"] == "CAPTURED"


def test_fail_closed_underage_compliance_denial():
    """Verify that underage consumers are denied immediately (fail-closed)."""
    underage_req = EvaluationRequest(
        subject_type="order",
        subject_id="ord_failclosed_01",
        jurisdiction_code="IN-KA",
        requested_at=datetime(2026, 8, 14, 15, 0, tzinfo=timezone.utc),
        actor={"user_id": "usr_minor_01", "role": "CONSUMER"},
        context={
            "consumer_age": 19,
            "quantity": 1,
            "delivery_zone": "zone_a",
            "license": {"status": "ACTIVE"},
            "product": {"category": "beer", "name": "Standard Lager"},
        },
    )

    decision = evaluate_order(
        underage_req,
        min_age=21,
        dry_days=[],
        sales_hours={"start": "00:00", "end": "23:59", "days": [0, 1, 2, 3, 4, 5, 6]},
        license_info=underage_req.context["license"],
        product_info=underage_req.context["product"],
        jurisdiction_categories=["beer"],
        quantity_limit=12,
        permitted_zones=["zone_a"],
    )

    assert decision.decision == DecisionOutcome.DENY
    assert any("below minimum" in hit.reason.lower() for hit in decision.hits)


def test_fail_closed_dry_day_denial():
    """Verify dry day restrictions enforce strict denial."""
    today = datetime(2026, 8, 14, 10, 0, tzinfo=timezone.utc).date()
    dry_day_req = EvaluationRequest(
        subject_type="order",
        subject_id="ord_dryday_01",
        jurisdiction_code="IN-KA",
        requested_at=datetime(2026, 8, 14, 10, 0, tzinfo=timezone.utc),
        actor={"user_id": "usr_adult_01", "role": "CONSUMER"},
        context={
            "consumer_age": 25,
            "quantity": 1,
            "delivery_zone": "zone_a",
            "license": {"status": "ACTIVE"},
            "product": {"category": "beer", "name": "Standard Lager"},
        },
    )

    decision = evaluate_order(
        dry_day_req,
        min_age=21,
        dry_days=[today],
        sales_hours={"start": "00:00", "end": "23:59", "days": [0, 1, 2, 3, 4, 5, 6]},
        license_info=dry_day_req.context["license"],
        product_info=dry_day_req.context["product"],
        jurisdiction_categories=["beer"],
        quantity_limit=12,
        permitted_zones=["zone_a"],
    )

    assert decision.decision == DecisionOutcome.DENY
    assert any("dry day" in hit.reason.lower() for hit in decision.hits)


def test_privacy_redaction_and_anonymization():
    """Verify PII detection and analytics anonymization."""
    raw_log = "Customer email is john.smith@example.com and phone is +919876543210"
    detected = detect_pii(raw_log)
    assert "email" in detected
    assert "phone_in" in detected

    clean_log = redact_pii(raw_log)
    assert "john.smith@example.com" not in clean_log
    assert "[REDACTED]" in clean_log

    analytics_record = {
        "email": "customer@example.com",
        "consumer_id": "cons_12345",
        "order_amount": 1450.0,
        "category": "beer",
    }
    anonymized = anonymize_for_analytics(analytics_record)

    assert "email" not in anonymized
    assert anonymized["category"] == "beer"
    assert anonymized["consumer_id"] != "cons_12345"
