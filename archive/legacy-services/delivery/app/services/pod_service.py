from datetime import datetime, timezone
from uuid import uuid4

from services.delivery.app.services.delivery_service import DeliveryService


class PodService:

    def __init__(self, delivery_service: DeliveryService | None = None):
        self.delivery_service = delivery_service or DeliveryService()
        self.pods: dict[str, dict] = {}

    async def complete_delivery(self, delivery_id: str, confirmation_method: str = "PIN_VERIFIED") -> dict:
        delivery = await self.delivery_service.get_delivery(delivery_id)
        if not delivery:
            raise ValueError("DELIVERY_NOT_FOUND")

        if delivery["status"] != "HANDED_OVER":
            raise ValueError("HANDOVER_REQUIRED")

        pod_id = str(uuid4())
        now = datetime.now(timezone.utc)
        pod = {
            "id": pod_id,
            "delivery_id": delivery_id,
            "verification_reference": f"ref_v_{delivery_id}",
            "handover_timestamp": now,
            "latitude": 19.0760,
            "longitude": 72.8777,
            "confirmation_method": confirmation_method,
        }
        self.pods[delivery_id] = pod

        await self.delivery_service.dispatch_service.transition(delivery, "COMPLETED")
        return pod
