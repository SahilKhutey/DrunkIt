import pytest
from services.observability.app.services.incident_service import IncidentService


@pytest.mark.asyncio
async def test_incident_lifecycle():
    svc = IncidentService()
    inc = await svc.create_incident("payment-service", "Payment Gateway Timeout", "CRITICAL")
    assert inc["status"] == "OPEN"
    assert inc["incident_code"].startswith("INC-")

    ack = await svc.acknowledge_incident(inc["id"], "operator-1")
    assert ack["status"] == "ACKNOWLEDGED"
    assert ack["assigned_to"] == "operator-1"

    res = await svc.resolve_incident(inc["id"])
    assert res["status"] == "RESOLVED"
    assert res["resolved_at"] is not None
