import pytest
from services.resilience.app.engine.recovery_engine import RecoveryEngine


@pytest.mark.asyncio
async def test_recovery_state_machine():
    engine = RecoveryEngine()
    res = await engine.recover("order-service")
    assert res["final_state"] == "COMPLETE"
    assert "DETECTED" in res["transitions"]
    assert "RESTORING" in res["transitions"]
    assert "COMPLETE" in res["transitions"]
