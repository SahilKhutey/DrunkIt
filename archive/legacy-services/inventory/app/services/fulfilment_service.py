from datetime import datetime, timezone
from uuid import uuid4

from services.inventory.app.domain.state import FULFILMENT_TRANSITIONS


class FulfilmentService:

    def __init__(self):
        self.fulfilments: dict[str, dict] = {}

    async def create(self, order_id: str, store_id: str) -> dict:
        fulfilment_id = str(uuid4())
        now = datetime.now(timezone.utc)
        fulfilment = {
            "id": fulfilment_id,
            "order_id": order_id,
            "store_id": store_id,
            "status": "CREATED",
            "assigned_to": None,
            "created_at": now,
            "updated_at": now,
        }
        self.fulfilments[fulfilment_id] = fulfilment
        return fulfilment

    async def transition(
        self,
        fulfilment_id: str,
        target_status: str,
    ) -> dict:

        fulfilment = self.fulfilments.get(fulfilment_id)
        if not fulfilment:
            raise ValueError("Fulfilment not found")

        current = fulfilment["status"]
        allowed = FULFILMENT_TRANSITIONS.get(current, set())

        if target_status not in allowed:
            raise ValueError(f"Invalid transition {current} -> {target_status}")

        fulfilment["status"] = target_status
        fulfilment["updated_at"] = datetime.now(timezone.utc)
        return fulfilment
