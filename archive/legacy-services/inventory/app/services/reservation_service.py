from datetime import datetime, timedelta, timezone
from uuid import uuid4

from services.inventory.app.schemas.reservation import ReservationCreate
from services.inventory.app.services.inventory_service import InventoryService


class ReservationService:

    RESERVATION_TTL_SECONDS = 600

    def __init__(self, inventory_service: InventoryService | None = None):
        self.inventory_service = inventory_service or InventoryService()
        self.reservations: dict[str, dict] = {}
        self.idempotency_map: dict[str, dict] = {}

    async def reserve(
        self,
        data: ReservationCreate,
    ) -> dict:

        if data.idempotency_key in self.idempotency_map:
            return self.idempotency_map[data.idempotency_key]

        available = await self.inventory_service.get_available(data.store_id, data.sku_id)

        if available < data.quantity:
            raise ValueError("INSUFFICIENT_STOCK")

        key = f"{data.store_id}:{data.sku_id}"
        inventory = self.inventory_service.inventory_store[key]
        inventory["reserved"] += data.quantity
        inventory["version"] += 1

        now = datetime.now(timezone.utc)
        res_id = str(uuid4())
        reservation = {
            "id": res_id,
            "order_id": data.order_id,
            "store_id": data.store_id,
            "sku_id": data.sku_id,
            "quantity": data.quantity,
            "status": "ACTIVE",
            "expires_at": now + timedelta(seconds=self.RESERVATION_TTL_SECONDS),
            "created_at": now,
        }

        self.reservations[res_id] = reservation
        self.idempotency_map[data.idempotency_key] = reservation
        return reservation

    async def release(
        self,
        reservation_id: str,
    ) -> dict:

        reservation = self.reservations.get(reservation_id)
        if not reservation:
            raise ValueError("Reservation not found")

        if reservation["status"] != "ACTIVE":
            return reservation

        key = f"{reservation['store_id']}:{reservation['sku_id']}"
        inventory = self.inventory_service.inventory_store.get(key)
        if inventory:
            inventory["reserved"] = max(0, inventory["reserved"] - reservation["quantity"])
            inventory["version"] += 1

        reservation["status"] = "RELEASED"
        return reservation

    async def confirm(
        self,
        reservation_id: str,
    ) -> dict:

        reservation = self.reservations.get(reservation_id)
        if not reservation:
            raise ValueError("Reservation not found")

        if reservation["status"] != "ACTIVE":
            return reservation

        reservation["status"] = "CONFIRMED"
        return reservation
