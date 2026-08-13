import pytest
from services.payment.app.schemas.payment import CreatePaymentRequest
from services.payment.app.services.payment_service import PaymentService
from services.payment.app.services.reconciliation_service import ReconciliationService


@pytest.mark.asyncio
async def test_reconciliation_matching():
    pay_svc = PaymentService()
    pay = await pay_svc.create_payment(
        CreatePaymentRequest(
            order_id="order-rec-1",
            customer_id="cust-100",
            amount=123000,
            currency="INR",
            idempotency_key="pay-key-rec-1",
        )
    )

    recon_svc = ReconciliationService(payment_service=pay_svc)

    provider_txs = [
        {"reference": pay["provider_payment_id"], "amount": 123000},
        {"reference": "missing-ref", "amount": 50000},
    ]

    records = await recon_svc.reconcile(provider_txs)
    assert len(records) == 2
    assert records[0]["status"] == "MATCHED"
    assert records[1]["status"] == "MISSING_INTERNAL"
