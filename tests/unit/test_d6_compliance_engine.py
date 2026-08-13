"""
Master unit test for Phase D6 Identity, Verification & Compliance Engine.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from services.compliance.app.schemas.compliance import ComplianceContext
from services.compliance.app.services.compliance_service import ComplianceService


@pytest.mark.asyncio
async def test_compliance_service_evaluation():
    service = ComplianceService()

    ctx_allow = ComplianceContext(
        consumer_id="consumer-101",
        retailer_id="retailer-505",
        jurisdiction="MAHARASHTRA",
        product_category="REGULATED_ALCOHOL",
        product_id="prod-77",
        quantity=1,
        delivery_latitude=19.0760,
        delivery_longitude=72.8777,
        order_value=1500.0,
    )

    decision = await service.evaluate(ctx_allow)
    assert decision.decision == "ALLOW"
    assert len(decision.reasons) == 0

    ctx_deny = ComplianceContext(
        consumer_id="consumer-101",
        retailer_id="invalid-retailer",
        jurisdiction="MAHARASHTRA",
        product_category="REGULATED_ALCOHOL",
        product_id="prod-77",
        quantity=1,
        delivery_latitude=19.0760,
        delivery_longitude=72.8777,
        order_value=1500.0,
    )

    decision_deny = await service.evaluate(ctx_deny)
    assert decision_deny.decision == "DENY"
    assert "No valid retailer licence" in decision_deny.reasons
