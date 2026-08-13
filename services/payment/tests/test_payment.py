import pytest
from services.payment.app.schemas.payment import CreatePaymentRequest
from services.payment.app.services.payment_service import PaymentService


@pytest.mark.asyncio
async def test_create_payment_success():
    svc = PaymentService()
    req = CreatePaymentRequest(
        order_id="order-100",
        customer_id="cust-100",
        amount=123000,
        currency="INR",
        idempotency_key="pay-key-100000",
    )

    pay = await svc.create_payment(req)
    assert pay["amount"] == 123000
    assert pay["status"] in ("AUTHORIZED", "CAPTURED")


@pytest.mark.asyncio
async def test_amount_tampering_blocked():
    svc = PaymentService()
    req = CreatePaymentRequest(
        order_id="order-tampered",
        customer_id="cust-100",
        amount=1,  # Client sends 0.01 INR while order is 500.00 INR
        currency="INR",
        idempotency_key="pay-key-tamper",
    )

    with pytest.raises(ValueError, match="AMOUNT_MISMATCH"):
        await svc.create_payment(req)
