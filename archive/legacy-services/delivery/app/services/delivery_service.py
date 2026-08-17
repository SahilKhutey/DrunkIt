from datetime import datetime, timezone

from services.delivery.app.services.dispatch_service import DispatchService
from services.delivery.app.state_machine.delivery_states import can_handover


class DeliveryService:

    def __init__(self, dispatch_service: DispatchService | None = None):
        self.dispatch_service = dispatch_service or DispatchService()

    async def get_delivery(self, delivery_id: str) -> dict | None:
        return self.dispatch_service.deliveries.get(delivery_id)

    async def handover(self, delivery_id: str) -> dict:
        delivery = await self.get_delivery(delivery_id)
        if not delivery:
            raise ValueError("DELIVERY_NOT_FOUND")

        if not can_handover(delivery):
            raise ValueError("FINAL_VERIFICATION_REQUIRED")

        await self.dispatch_service.transition(delivery, "HANDED_OVER")
        return delivery

    async def fail_delivery(self, delivery_id: str, reason: str, notes: str | None = None) -> dict:
        delivery = await self.get_delivery(delivery_id)
        if not delivery:
            raise ValueError("DELIVERY_NOT_FOUND")

        if delivery["status"] not in ("IN_TRANSIT", "ARRIVING", "VERIFICATION_PENDING", "VERIFIED"):
            raise ValueError("INVALID_FAILURE_STATE")

        delivery["status"] = "DELIVERY_FAILED"
        delivery["failure_reason"] = reason
        delivery["failure_notes"] = notes
        delivery["updated_at"] = datetime.now(timezone.utc)
        return delivery

    async def initiate_return(self, delivery_id: str) -> dict:
        delivery = await self.get_delivery(delivery_id)
        if not delivery:
            raise ValueError("DELIVERY_NOT_FOUND")

        if delivery["status"] != "DELIVERY_FAILED":
            raise ValueError("RETURN_NOT_REQUIRED")

        await self.dispatch_service.transition(delivery, "RETURN_REQUIRED")
        return delivery
