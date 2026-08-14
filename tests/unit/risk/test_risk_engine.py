"""Unit tests for RiskScoringEngine and rules."""

import uuid
from decimal import Decimal
from services.risk.app.schemas.risk import RiskEvaluationRequest
from services.risk.app.services.scoring import RiskScoringEngine


def test_low_risk_is_allowed():
    engine = RiskScoringEngine()
    req = RiskEvaluationRequest(
        order_id=uuid.uuid4(),
        consumer_id=uuid.uuid4(),
        amount=Decimal("1000.00"),
        failed_payments=0,
        recent_order_count=1,
        device_trust_score=0.95,
    )
    res = engine.evaluate(req)
    assert res.decision.value == "allow"
    assert res.risk_level.value == "low"
    assert res.score == 0.0


def test_high_velocity_is_blocked():
    engine = RiskScoringEngine()
    req = RiskEvaluationRequest(
        order_id=uuid.uuid4(),
        consumer_id=uuid.uuid4(),
        amount=Decimal("55000.00"),
        failed_payments=5,
        recent_order_count=15,
        device_trust_score=0.1,
    )
    res = engine.evaluate(req)
    assert res.decision.value == "block"
    assert res.score >= 0.70
    assert "high_failed_payment_velocity" in res.reasons
