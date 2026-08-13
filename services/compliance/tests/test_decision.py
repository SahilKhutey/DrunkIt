import pytest
from services.compliance.app.services.decision_engine import DecisionEngine


@pytest.mark.asyncio
async def test_unverified_consumer_is_blocked():
    checks = [
        {"status": "PASS"},
        {
            "status": "DENY",
            "reason": "Consumer eligibility verification failed",
        },
    ]

    engine = DecisionEngine()
    result = await engine.decide(checks)

    assert result["decision"] == "DENY"
    assert "Consumer eligibility verification failed" in result["reasons"]
