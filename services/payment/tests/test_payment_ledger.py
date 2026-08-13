import pytest
from services.payment.app.services.ledger_service import LedgerService


@pytest.mark.asyncio
async def test_double_entry_ledger_balancing():
    ledger = LedgerService()

    payment = {
        "id": "pay-1",
        "order_id": "ord-1",
        "amount": 100000,
        "currency": "INR",
    }

    tx = await ledger.record_payment(payment)
    is_valid = await ledger.validate_transaction(tx["id"])
    assert is_valid is True
