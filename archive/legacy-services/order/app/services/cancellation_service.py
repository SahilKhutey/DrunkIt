from datetime import datetime, timezone

from services.order.app.domain.state import CANCELLABLE_STATES
from services.order.app.services.order_service import OrderService


class CancellationService:

    def __init__(self, order_service: OrderService | None = None):
        self.order_service = order_service or OrderService()

    async def cancel(
        self,
        order_id: str,
        reason: str = "CUSTOMER_CANCELLED",
        customer_id: str | None = None,
    ) -> dict:

        order = await self.order_service.get(order_id, customer_id=customer_id)
        if not order:
            raise ValueError("ORDER_NOT_FOUND")

        if order["status"] not in CANCELLABLE_STATES:
            raise ValueError("ORDER_NOT_CANCELLABLE")

        order["status"] = "CANCELLED"
        order["cancellation_reason"] = reason
        order["updated_at"] = datetime.now(timezone.utc)
        return order
