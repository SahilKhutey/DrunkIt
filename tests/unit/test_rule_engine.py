"""Unit tests for the pure rule engine."""

from __future__ import annotations

import sys
import os

for k in list(sys.modules.keys()):
    if k == "app" or k.startswith("app."):
        sys.modules.pop(k, None)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../services/compliance-service")))

from datetime import date, datetime, timezone
import pytest

from app.domain.rule_engine import (
    DecisionOutcome, EvaluationRequest, evaluate_order,
)


def make_request(**overrides) -> EvaluationRequest:
    base = {
        "subject_type": "order",
        "subject_id": "ord_123",
        "jurisdiction_code": "IN-CG",
        "requested_at": datetime(2025, 1, 15, 14, 0, tzinfo=timezone.utc),
        "actor": {"user_id": "u_1", "role": "CONSUMER"},
        "context": {
            "consumer_age": 25,
            "quantity": 2,
            "delivery_zone": "zone_a",
            "license": {"status": "ACTIVE", "valid_until": "2026-12-31T00:00:00Z"},
            "product": {"category": "beer", "name": "Test Beer"},
        },
    }
    base["context"].update(overrides.get("context", {}))
    base.update({k: v for k, v in overrides.items() if k != "context"})
    return EvaluationRequest(**base)


def test_all_pass() -> None:
    req = make_request()
    result = evaluate_order(
        req,
        min_age=21, dry_days=[],
        sales_hours={"start": "00:00", "end": "23:59", "days": [0,1,2,3,4,5,6]},
        license_info=req.context["license"],
        product_info=req.context["product"],
        jurisdiction_categories=["beer", "wine", "spirit"],
        quantity_limit=12, permitted_zones=["zone_a"],
    )
    assert result.decision == DecisionOutcome.ALLOW
    assert result.confidence == 1.0


def test_dry_day_denies() -> None:
    req = make_request()
    result = evaluate_order(
        req, min_age=21,
        dry_days=[req.requested_at.date()],
        sales_hours={"start": "00:00", "end": "23:59", "days": [0,1,2,3,4,5,6]},
        license_info=req.context["license"],
        product_info=req.context["product"],
        jurisdiction_categories=["beer"], quantity_limit=12, permitted_zones=["zone_a"],
    )
    assert result.decision == DecisionOutcome.DENY
    assert any("dry day" in h.reason.lower() for h in result.hits)


def test_underage_denies() -> None:
    req = make_request(context={"consumer_age": 18})
    result = evaluate_order(
        req, min_age=21, dry_days=[],
        sales_hours={"start": "00:00", "end": "23:59", "days": [0,1,2,3,4,5,6]},
        license_info=req.context["license"],
        product_info=req.context["product"],
        jurisdiction_categories=["beer"], quantity_limit=12, permitted_zones=["zone_a"],
    )
    assert result.decision == DecisionOutcome.DENY
    assert any("below minimum" in h.reason.lower() for h in result.hits)


def test_no_age_verified_denies() -> None:
    req = make_request(context={"consumer_age": None})
    result = evaluate_order(
        req, min_age=21, dry_days=[],
        sales_hours={"start": "00:00", "end": "23:59", "days": [0,1,2,3,4,5,6]},
        license_info=req.context["license"],
        product_info=req.context["product"],
        jurisdiction_categories=["beer"], quantity_limit=12, permitted_zones=["zone_a"],
    )
    assert result.decision == DecisionOutcome.DENY


def test_expired_license_denies() -> None:
    req = make_request(context={"license": {"status": "EXPIRED"}})
    result = evaluate_order(
        req, min_age=21, dry_days=[],
        sales_hours={"start": "00:00", "end": "23:59", "days": [0,1,2,3,4,5,6]},
        license_info=req.context["license"],
        product_info=req.context["product"],
        jurisdiction_categories=["beer"], quantity_limit=12, permitted_zones=["zone_a"],
    )
    assert result.decision == DecisionOutcome.DENY


def test_quantity_exceeded_denies() -> None:
    req = make_request(context={"quantity": 20})
    result = evaluate_order(
        req, min_age=21, dry_days=[],
        sales_hours={"start": "00:00", "end": "23:59", "days": [0,1,2,3,4,5,6]},
        license_info=req.context["license"],
        product_info=req.context["product"],
        jurisdiction_categories=["beer"], quantity_limit=12, permitted_zones=["zone_a"],
    )
    assert result.decision == DecisionOutcome.DENY
    assert any("quantity" in h.reason.lower() for h in result.hits)


def test_wrong_zone_denies() -> None:
    req = make_request(context={"delivery_zone": "zone_x"})
    result = evaluate_order(
        req, min_age=21, dry_days=[],
        sales_hours={"start": "00:00", "end": "23:59", "days": [0,1,2,3,4,5,6]},
        license_info=req.context["license"],
        product_info=req.context["product"],
        jurisdiction_categories=["beer"], quantity_limit=12, permitted_zones=["zone_a"],
    )
    assert result.decision == DecisionOutcome.DENY


def test_unauthorized_product_denies() -> None:
    req = make_request(context={"product": {"category": "nuclear_material"}})
    result = evaluate_order(
        req, min_age=21, dry_days=[],
        sales_hours={"start": "00:00", "end": "23:59", "days": [0,1,2,3,4,5,6]},
        license_info=req.context["license"],
        product_info=req.context["product"],
        jurisdiction_categories=["beer"], quantity_limit=12, permitted_zones=["zone_a"],
    )
    assert result.decision == DecisionOutcome.DENY


def test_outside_hours_denies() -> None:
    req = make_request()
    req.requested_at = datetime(2025, 1, 15, 23, 30, tzinfo=timezone.utc)
    result = evaluate_order(
        req, min_age=21, dry_days=[],
        sales_hours={"start": "10:00", "end": "22:00", "days": [0,1,2,3,4,5,6]},
        license_info=req.context["license"],
        product_info=req.context["product"],
        jurisdiction_categories=["beer"], quantity_limit=12, permitted_zones=["zone_a"],
    )
    assert result.decision == DecisionOutcome.DENY
