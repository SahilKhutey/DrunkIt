import pytest
from services.security.app.engine.risk_engine import RiskEngine
from services.security.app.models.enums import RiskDecision, RiskLevel


@pytest.mark.asyncio
async def test_risk_engine_scoring_and_decisions():
    engine = RiskEngine()
    signals = [
        {"signal_type": "NEW_DEVICE", "score": 15.0},
        {"signal_type": "PASSWORD_RESET", "score": 20.0},
        {"signal_type": "ORDER_VELOCITY", "score": 50.0},
    ]

    res = await engine.evaluate("CONSUMER", "user-d13-1", signals=signals)
    assert res["risk_score"] == 85.0
    assert res["risk_level"] == RiskLevel.CRITICAL.value
    assert res["decision"] == RiskDecision.BLOCK.value
