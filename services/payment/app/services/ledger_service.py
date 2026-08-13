from datetime import datetime, timezone
from uuid import uuid4


class LedgerService:

    def __init__(self):
        self.transactions: dict[str, dict] = {}
        self.entries: dict[str, list[dict]] = {}

    async def record_payment(self, payment: dict) -> dict:
        tx_id = str(uuid4())
        now = datetime.now(timezone.utc)
        transaction = {
            "id": tx_id,
            "transaction_type": "PAYMENT",
            "reference_type": "ORDER",
            "reference_id": str(payment["order_id"]),
            "amount": payment["amount"],
            "currency": payment.get("currency", "INR"),
            "status": "COMPLETED",
            "idempotency_key": f"payment:{payment['id']}",
            "created_at": now,
        }
        self.transactions[tx_id] = transaction

        ledger_entries = [
            {
                "id": str(uuid4()),
                "transaction_id": tx_id,
                "account_id": "payment_processor",
                "entry_type": "DEBIT",
                "amount": payment["amount"],
                "currency": payment.get("currency", "INR"),
                "created_at": now,
            },
            {
                "id": str(uuid4()),
                "transaction_id": tx_id,
                "account_id": "customer_order",
                "entry_type": "CREDIT",
                "amount": payment["amount"],
                "currency": payment.get("currency", "INR"),
                "created_at": now,
            },
        ]
        self.entries[tx_id] = ledger_entries
        return transaction

    async def validate_transaction(self, transaction_id: str) -> bool:
        entries = self.entries.get(transaction_id, [])
        debit = sum(e["amount"] for e in entries if e["entry_type"] == "DEBIT")
        credit = sum(e["amount"] for e in entries if e["entry_type"] == "CREDIT")

        if debit != credit:
            raise ValueError("LEDGER_IMBALANCE")
        return True
