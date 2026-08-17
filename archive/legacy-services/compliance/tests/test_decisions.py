import pytest
from datetime import datetime, timezone
from services.compliance.app.engine.context import ComplianceContext
from services.compliance.app.engine.decision_engine import DecisionEngine
from services.compliance.app.services.policy_service import PolicyService


@pytest.mark.asyncio
async def test_3way_decision_engine_unverified_deny():
    pol_svc = PolicyService()
    dec_engine = DecisionEngine(policy_service=pol_svc)

    ctx = ComplianceContext(
        consumer_id="cons-unverified-1",
        retailer_id=None,
        rider_id=None,
        product_id=None,
        order_id=None,
        delivery_id=None,
        jurisdiction_id="IN-STATE-X",
        operation="CREATE_ALCOHOL_ORDER",
        timestamp=datetime.now(timezone.utc),
    )
    setattr(ctx, "consumer_verification_status", "UNVERIFIED")

    res = await dec_engine.decide(ctx)
    assert res["decision"] == "DENY"
    assert len(res["reasons"]) > 0
