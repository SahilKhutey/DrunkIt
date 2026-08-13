from uuid import uuid4

from services.payment.app.gateways.base import PaymentGateway
from services.payment.app.gateways.mock import MockGateway
from services.payment.app.services.payment_service import PaymentService


class RefundService:

    def __init__(
        self,
        payment_service: PaymentService | None = None,
        gateway: PaymentGateway | None = None,
    ):
        self.payment_service = payment_service or PaymentService()
        self.gateway = gateway or MockGateway()

        self.refunds: dict[str, dict] = {}
        self.idempotency_map: dict[str, dict] = {}

    async def refund(
        self,
        payment_id: str,
        amount: int,
        idempotency_key: str,
    ) -> dict:

        if idempotency_key in self.idempotency_map:
            return self.idempotency_map[idempotency_key]

        payment = self.payment_service.payments.get(payment_id)
        if not payment:
            raise ValueError("PAYMENT_NOT_FOUND")

        if payment["status"] not in ("CAPTURED", "PARTIALLY_REFUNDED"):
            raise ValueError("PAYMENT_NOT_REFUNDABLE")

        already_refunded = sum(
            r["amount"]
            for r in self.refunds.values()
            if r["payment_id"] == payment_id and r["status"] in ("REFUNDED", "COMPLETED")
        )

        remaining = payment["amount"] - already_refunded
        if amount > remaining:
            raise ValueError("REFUND_EXCEEDS_REMAINING")

        result = await self.gateway.refund(
            provider_payment_id=payment["provider_payment_id"],
            amount=amount,
            idempotency_key=idempotency_key,
        )

        refund_id = str(uuid4())
        refund_record = {
            "id": refund_id,
            "payment_id": payment_id,
            "order_id": payment["order_id"],
            "amount": amount,
            "status": result["status"],
            "provider_refund_id": result.get("provider_refund_id"),
            "idempotency_key": idempotency_key,
        }

        self.refunds[refund_id] = refund_record
        self.idempotency_map[idempotency_key] = refund_record

        refunded_total = already_refunded + amount
        if refunded_total == payment["amount"]:
            payment["status"] = "REFUNDED"
        else:
            payment["status"] = "PARTIALLY_REFUNDED"

        return refund_record
