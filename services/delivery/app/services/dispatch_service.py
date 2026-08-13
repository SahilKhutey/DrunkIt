from datetime import datetime, timezone
from uuid import uuid4

from services.delivery.app.schemas.delivery import DeliveryCreate
from services.delivery.app.state_machine.delivery_states import DELIVERY_TRANSITIONS


class DispatchService:

    def __init__(self):
        self.deliveries: dict[str, dict] = {}
        self.dispatch_jobs: dict[str, dict] = {}

    async def create_delivery(self, data: DeliveryCreate) -> dict:
        for d in self.deliveries.values():
            if d["order_id"] == data.order_id:
                return d

        delivery_id = str(uuid4())
        now = datetime.now(timezone.utc)
        delivery = {
            "id": delivery_id,
            "order_id": data.order_id,
            "retailer_id": data.retailer_id,
            "status": "CREATED",
            "delivery_address_id": data.delivery_address_id,
            "verification_required": data.regulated_product,
            "eta_seconds": 600,
            "created_at": now,
            "updated_at": now,
        }
        self.deliveries[delivery_id] = delivery
        return delivery

    async def transition(self, delivery: dict, target_status: str) -> dict:
        current = delivery["status"]
        allowed = DELIVERY_TRANSITIONS.get(current, set())
        if target_status not in allowed:
            raise ValueError(f"Invalid transition {current} -> {target_status}")

        delivery["status"] = target_status
        delivery["updated_at"] = datetime.now(timezone.utc)
        return delivery

    async def queue_dispatch(self, delivery_id: str, priority: int = 100) -> dict:
        delivery = self.deliveries.get(delivery_id)
        if not delivery:
            raise ValueError("DELIVERY_NOT_FOUND")

        if delivery["status"] != "CREATED":
            raise ValueError("DELIVERY_NOT_READY")

        await self.transition(delivery, "READY_FOR_DISPATCH")

        job_id = str(uuid4())
        job = {
            "id": job_id,
            "delivery_id": delivery_id,
            "retailer_id": delivery["retailer_id"],
            "priority": priority,
            "status": "QUEUED",
            "idempotency_key": f"dispatch:{delivery_id}",
            "created_at": datetime.now(timezone.utc),
        }
        self.dispatch_jobs[job_id] = job

        await self.transition(delivery, "DISPATCH_QUEUED")
        await self.transition(delivery, "ASSIGNMENT_PENDING")
        return job
