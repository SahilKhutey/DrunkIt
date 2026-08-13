from datetime import datetime, timezone
from uuid import uuid4

from services.payment.app.clients.order_client import OrderClient
from services.payment.app.domain.state import PAYMENT_TRANSITIONS
from services.payment.app.gateways.base import PaymentGateway
from services.payment.app.gateways.mock import MockGateway
from services.payment.app.schemas.payment import CreatePaymentRequest
from services.payment.app.services.ledger_service import LedgerService


class PaymentService:

    def __init__(
        self,
        order_client: OrderClient | None = None,
        gateway: PaymentGateway | None = None,
        ledger_service: LedgerService | None = None,
    ):
        self.orders = order_client or OrderClient()
        self.gateway = gateway or MockGateway()
        self.ledger = ledger_service or LedgerService()

        self.payments: dict[str, dict] = {}
        self.idempotency_map: dict[str, dict] = {}

    async def create_payment(self, request: CreatePaymentRequest) -> dict:
        # 1. Idempotency check
        if request.idempotency_key in self.idempotency_map:
            return self.idempotency_map[request.idempotency_key]

        # 2. Load authoritative order
        order = await self.orders.get_order(request.order_id)
        if not order:
            raise ValueError("ORDER_NOT_FOUND")

        # 3. Verify ownership
        if str(order.customer_id) != request.customer_id:
            raise ValueError("ORDER_ACCESS_DENIED")

        # 4. Verify amount against authoritative order total
        if request.amount != order.total:
            raise ValueError("AMOUNT_MISMATCH")

        # 5. Verify order state
        if order.status != "PENDING_PAYMENT":
            raise ValueError("ORDER_NOT_PAYABLE")

        # 6. Create Payment Record
        payment_id = str(uuid4())
        now = datetime.now(timezone.utc)
        payment = {
            "id": payment_id,
            "order_id": order.id,
            "customer_id": order.customer_id,
            "amount": order.total,
            "currency": order.currency,
            "status": "PENDING",
            "provider": "mock",
            "provider_payment_id": None,
            "idempotency_key": request.idempotency_key,
            "created_at": now,
            "updated_at": now,
        }

        # 7. Provider call
        result = await self.gateway.create_payment(
            amount=order.total,
            currency=order.currency,
            order_id=str(order.id),
            idempotency_key=request.idempotency_key,
        )

        # 8. Update payment status & provider_payment_id
        payment["provider_payment_id"] = result["provider_payment_id"]
        payment["status"] = result["status"]
        payment["updated_at"] = datetime.now(timezone.utc)

        self.payments[payment_id] = payment
        self.idempotency_map[request.idempotency_key] = payment

        # Record double-entry ledger entry
        if result["status"] in ("AUTHORIZED", "CAPTURED"):
            await self.ledger.record_payment(payment)

        return payment

    async def transition_payment(self, payment: dict, new_status: str) -> dict:
        allowed = PAYMENT_TRANSITIONS.get(payment["status"], set())
        if new_status not in allowed:
            raise ValueError(f"Invalid payment transition {payment['status']} -> {new_status}")

        payment["status"] = new_status
        payment["updated_at"] = datetime.now(timezone.utc)
        return payment

    async def capture_payment(self, payment_id: str) -> dict:
        payment = self.payments.get(payment_id)
        if not payment:
            raise ValueError("PAYMENT_NOT_FOUND")

        if payment["status"] == "CAPTURED":
            return payment

        if payment["status"] != "AUTHORIZED":
            raise ValueError("PAYMENT_NOT_CAPTUREABLE")

        result = await self.gateway.capture(
            provider_payment_id=payment["provider_payment_id"],
            amount=payment["amount"],
        )

        if result["status"] != "CAPTURED":
            await self.transition_payment(payment, "FAILED")
            raise ValueError("PAYMENT_CAPTURE_FAILED")

        await self.transition_payment(payment, "CAPTURED")
        return payment
