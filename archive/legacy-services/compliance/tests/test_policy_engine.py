import pytest
from services.compliance.app.engine.context import ComplianceContext
from services.compliance.app.engine.rule_engine import RuleEngine


def test_rule_evaluator_operators():
    engine = RuleEngine()

    assert engine.evaluate_condition("VERIFIED", "equals", "VERIFIED") is True
    assert engine.evaluate_condition("UNVERIFIED", "equals", "VERIFIED") is False
    assert engine.evaluate_condition(21, "greater_equal", 21) is True
    assert engine.evaluate_condition(20, "greater_equal", 21) is False
    assert engine.evaluate_condition("STATE-A", "in", ["STATE-A", "STATE-B"]) is True


def test_rule_engine_evaluate():
    engine = RuleEngine()
    ctx = ComplianceContext(
        consumer_id="c1",
        retailer_id=None,
        rider_id=None,
        product_id=None,
        order_id=None,
        delivery_id=None,
        jurisdiction_id="IN-STATE-X",
        operation="CREATE_ALCOHOL_ORDER",
        timestamp=None,
    )
    setattr(ctx, "consumer_verification_status", "UNVERIFIED")

    rules = [
        {
            "id": "consumer_verification",
            "type": "REQUIREMENT",
            "condition": {
                "field": "consumer_verification_status",
                "operator": "equals",
                "value": "VERIFIED",
            },
            "failure": "DENY",
            "message": "Age/identity unverified",
        }
    ]

    results = engine.evaluate(ctx, rules)
    assert len(results) == 1
    assert results[0]["passed"] is False
    assert results[0]["failure_action"] == "DENY"
