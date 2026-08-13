from datetime import datetime, timezone

from services.order.app.clients.payment_client import PaymentClient
from services.order.app.domain.state import ORDER_TRANSITIONS
from services.order.app.services.checkout_service import CheckoutService


class OrderService:

    def __init__(
        self,
        checkout_service: CheckoutService | None = None,
        payment_client: PaymentClient | None = None,
    ):
        self.checkout_service = checkout_service or CheckoutService()
        self.payment_client = payment_client or PaymentClient()

    async def get(self, order_id: str, customer_id: str | None = None) -> dict | None:
        order = self.checkout_service.orders.get(order_id)
        if not order:
            return None
        if customer_id and order["customer_id"] != customer_id:
            raise PermissionError("ORDER_ACCESS_DENIED")
        return order

    async def transition(self, order_id: str, target_status: str) -> dict:
        order = await self.get(order_id)
        if not order:
            raise ValueError("ORDER_NOT_FOUND")

        current = order["status"]
        allowed = ORDER_TRANSITIONS.get(current, set())
        if target_status not in allowed:
            raise ValueError(f"Invalid transition: {current} -> {target_status}")

        order["status"] = target_status
        order["updated_at"] = datetime.now(timezone.utc)
        return order

    async def complete_payment(self, order_id: str, payment_id: str) -> dict:
        order = await self.get(order_id)
        if not order:
            raise ValueError("ORDER_NOT_FOUND")

        if order["status"] != "PENDING_PAYMENT":
            return order

        payment = await self.payment_client.get_status(payment_id)

        if payment.status != "AUTHORIZED":
            order["status"] = "PAYMENT_FAILED"
            order["updated_at"] = datetime.now(timezone.utc)
            return order

        order["status"] = "PAYMENT_AUTHORIZED"
        order["status"] = "CONFIRMED"
        order["updated_at"] = datetime.now(timezone.utc)
        return order
