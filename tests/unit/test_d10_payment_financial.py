"""
Master unit test for Phase D10 Payment + Financial Transaction Engine.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from services.payment.app.schemas.payment import CreatePaymentRequest
from services.payment.app.services.payment_service import PaymentService
from services.payment.app.services.payout_service import PayoutService
from services.payment.app.services.refund_service import RefundService


@pytest.mark.asyncio
async def test_full_d10_payment_financial_flow():
    pay_svc = PaymentService()

    # 1. Create Payment
    pay = await pay_svc.create_payment(
        CreatePaymentRequest(
            order_id="order-d10-master",
            customer_id="cust-100",
            amount=123000,
            currency="INR",
            idempotency_key="pay-key-master-d10",
        )
    )
    assert pay["status"] in ("AUTHORIZED", "CAPTURED")

    # 2. Capture Payment
    captured = await pay_svc.capture_payment(pay["id"])
    assert captured["status"] == "CAPTURED"

    # 3. Partial Refund
    ref_svc = RefundService(payment_service=pay_svc)
    refund = await ref_svc.refund(
        payment_id=pay["id"],
        amount=30000,
        idempotency_key="ref-key-master-d10",
    )
    assert refund["status"] == "REFUNDED"
    assert pay["status"] == "PARTIALLY_REFUNDED"

    # 4. Payout calculation
    payout_svc = PayoutService()
    payable = await payout_svc.calculate_payout(
        retailer_id="ret-01",
        eligible_sales=123000,
        refunds=30000,
        platform_fee_pct=0.05,
    )
    # Net: 93000, Fee: 4650, Payable: 88350
    assert payable == 88350
