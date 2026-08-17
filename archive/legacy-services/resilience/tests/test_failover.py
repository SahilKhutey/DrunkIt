import pytest
from services.resilience.app.services.failover_service import FailoverService


@pytest.mark.asyncio
async def test_failover_execution():
    svc = FailoverService()
    res = await svc.execute_failover("order-service", "region-a", "region-b")
    assert res["status"] == "COMPLETED"
    assert res["active"] == "region-b"
