import pytest
from services.compliance.app.services.risk_service import RiskService


@pytest.mark.asyncio
async def test_risk_scoring():
    svc = RiskService()
    await svc.record_signal("CONSUMER", "cons-risk-1", "VELOCITY_ANOMALY", "MEDIUM", 45.0)
    await svc.record_signal("CONSUMER", "cons-risk-1", "LOCATION_ANOMALY", "HIGH", 40.0)

    res = await svc.evaluate_risk("cons-risk-1")
    assert res["score"] == 85.0
    assert res["level"] == "HIGH"
