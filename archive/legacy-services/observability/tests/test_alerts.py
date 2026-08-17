import pytest
from services.observability.app.engine.alert_engine import AlertEngine
from services.observability.app.services.alert_service import AlertService


def test_alert_engine_operators():
    engine = AlertEngine()
    assert engine.evaluate(0.08, 0.05, "greater_than") is True
    assert engine.evaluate(0.03, 0.05, "greater_than") is False
    assert engine.evaluate(10, 20, "less_than") is True


@pytest.mark.asyncio
async def test_alert_service_deduplication():
    svc = AlertService()
    a1 = await svc.create_alert("HIGH_ERROR_RATE", "order-service", "HIGH", "Error rate > 5%")
    a2 = await svc.create_alert("HIGH_ERROR_RATE", "order-service", "HIGH", "Error rate > 5%")

    assert a1["fingerprint"] == a2["fingerprint"]
    assert a2["count"] == 2
