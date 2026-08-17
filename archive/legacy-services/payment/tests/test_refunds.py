import pytest
from services.payment.app.schemas.payment import CreatePaymentRequest
from services.payment.app.services.payment_service import PaymentService
from services.payment.app.services.refund_service import RefundService


@pytest.mark.asyncio
async def test_refund_lifecycle_and_limit_enforcement():
    pay_svc = PaymentService()
    pay = await pay_svc.create_payment(
        CreatePaymentRequest(
            order_id="order-ref",
            customer_id="cust-100",
            amount=123000,
            currency="INR",
            idempotency_key="pay-key-refund123",
        )
    )

    # Capture payment
    captured = await pay_svc.capture_payment(pay["id"])
    assert captured["status"] == "CAPTURED"

    ref_svc = RefundService(payment_service=pay_svc)

    # Over-refund attempt
    with pytest.raises(ValueError, match="REFUND_EXCEEDS_REMAINING"):
        await ref_svc.refund(
            payment_id=pay["id"],
            amount=200000,
            idempotency_key="ref-overfund-key",
        )

    # Valid refund
    ref = await ref_svc.refund(
        payment_id=pay["id"],
        amount=50000,
        idempotency_key="ref-valid-key",
    )
    assert ref["status"] == "REFUNDED"
    assert pay["status"] == "PARTIALLY_REFUNDED"
