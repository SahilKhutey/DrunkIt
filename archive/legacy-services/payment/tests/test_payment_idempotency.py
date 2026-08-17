import pytest
from services.payment.app.schemas.payment import CreatePaymentRequest
from services.payment.app.services.payment_service import PaymentService


@pytest.mark.asyncio
async def test_payment_idempotency():
    svc = PaymentService()
    req = CreatePaymentRequest(
        order_id="order-idemp-100",
        customer_id="cust-100",
        amount=123000,
        currency="INR",
        idempotency_key="pay-key-idemp-unique",
    )

    first = await svc.create_payment(req)
    second = await svc.create_payment(req)

    assert first["id"] == second["id"]
    assert first["status"] == second["status"]
