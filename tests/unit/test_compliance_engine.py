import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../services/compliance-service")))

import pytest
from compliance_app.models import ComplianceEvaluationRequest, OrderItemCompliance, DecisionResult
from compliance_app.engine import evaluate_compliance

def test_karnataka_age_eligibility():
    # Age eligible consumer in Karnataka
    req = ComplianceEvaluationRequest(
        consumer_id="C-1001",
        consumer_age_eligible=True,
        store_id="STR-BANGALORE-01",
        jurisdiction="IN-KA",
        license_status="ACTIVE",
        order_timestamp_iso="2026-08-11T14:30:00Z",
        items=[
            OrderItemCompliance(category="SPIRITS", abv=42.8, quantity=1, volume_ml=750)
        ]
    )
    result, reasons, policy_ver = evaluate_compliance(req)
    assert result == DecisionResult.ALLOW
    assert "passed successfully" in reasons[0]

def test_underage_denial():
    # Ineligible consumer
    req = ComplianceEvaluationRequest(
        consumer_id="C-9999",
        consumer_age_eligible=False,
        store_id="STR-BANGALORE-01",
        jurisdiction="IN-KA",
        license_status="ACTIVE",
        order_timestamp_iso="2026-08-11T14:30:00Z",
        items=[
            OrderItemCompliance(category="BEER", abv=5.0, quantity=1, volume_ml=500)
        ]
    )
    result, reasons, policy_ver = evaluate_compliance(req)
    assert result == DecisionResult.DENY
    assert any("not age-eligible" in r for r in reasons)

def test_dry_day_denial():
    # Order attempt on Gandhi Jayanti (Oct 2)
    req = ComplianceEvaluationRequest(
        consumer_id="C-1001",
        consumer_age_eligible=True,
        store_id="STR-BANGALORE-01",
        jurisdiction="IN-KA",
        license_status="ACTIVE",
        order_timestamp_iso="2026-10-02T12:00:00Z",
        items=[
            OrderItemCompliance(category="WINE", abv=13.0, quantity=1, volume_ml=750)
        ]
    )
    result, reasons, policy_ver = evaluate_compliance(req)
    assert result == DecisionResult.DENY
    assert any("prohibited dry day" in r for r in reasons)
