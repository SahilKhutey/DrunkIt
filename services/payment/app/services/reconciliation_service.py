from datetime import datetime, timezone
from uuid import uuid4

from services.payment.app.domain.state import ReconciliationStatus
from services.payment.app.services.payment_service import PaymentService


class ReconciliationService:

    def __init__(self, payment_service: PaymentService | None = None):
        self.payment_service = payment_service or PaymentService()
        self.reconciliation_records: list[dict] = []

    async def reconcile(self, provider_transactions: list[dict]) -> list[dict]:
        results = []

        for provider_tx in provider_transactions:
            provider_ref = provider_tx["reference"]
            provider_amount = provider_tx["amount"]

            internal = None
            for p in self.payment_service.payments.values():
                if p.get("provider_payment_id") == provider_ref or str(p.get("order_id")) == provider_ref:
                    internal = p
                    break

            if not internal:
                rec = {
                    "id": str(uuid4()),
                    "provider": "mock",
                    "provider_reference": provider_ref,
                    "internal_reference": None,
                    "provider_amount": provider_amount,
                    "internal_amount": None,
                    "status": ReconciliationStatus.MISSING_INTERNAL,
                    "created_at": datetime.now(timezone.utc),
                }
                self.reconciliation_records.append(rec)
                results.append(rec)
                continue

            if internal["amount"] != provider_amount:
                rec = {
                    "id": str(uuid4()),
                    "provider": "mock",
                    "provider_reference": provider_ref,
                    "internal_reference": internal["id"],
                    "provider_amount": provider_amount,
                    "internal_amount": internal["amount"],
                    "status": ReconciliationStatus.AMOUNT_MISMATCH,
                    "created_at": datetime.now(timezone.utc),
                }
                self.reconciliation_records.append(rec)
                results.append(rec)
                continue

            rec = {
                "id": str(uuid4()),
                "provider": "mock",
                "provider_reference": provider_ref,
                "internal_reference": internal["id"],
                "provider_amount": provider_amount,
                "internal_amount": internal["amount"],
                "status": ReconciliationStatus.MATCHED,
                "created_at": datetime.now(timezone.utc),
            }
            self.reconciliation_records.append(rec)
            results.append(rec)

        return results
