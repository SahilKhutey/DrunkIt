from datetime import datetime, timezone
from uuid import uuid4

from services.inventory.app.schemas.inventory import StockAdjustment, StockReceipt


class InventoryService:

    def __init__(self, session_factory=None):
        self.session_factory = session_factory
        self.inventory_store: dict[str, dict] = {}
        self.ledger_store: dict[str, dict] = {}

    async def get_available(
        self,
        store_id: str,
        sku_id: str,
    ) -> int:

        key = f"{store_id}:{sku_id}"
        item = self.inventory_store.get(key)
        if not item:
            return 0
        return max(
            0,
            item["on_hand"] - item["reserved"] - item["damaged"] - item["blocked"],
        )

    async def receive_stock(
        self,
        data: StockReceipt,
    ) -> dict:

        if data.idempotency_key in self.ledger_store:
            return self.ledger_store[data.idempotency_key]

        key = f"{data.store_id}:{data.sku_id}"
        now = datetime.now(timezone.utc)

        if key not in self.inventory_store:
            self.inventory_store[key] = {
                "id": str(uuid4()),
                "store_id": data.store_id,
                "sku_id": data.sku_id,
                "on_hand": 0,
                "reserved": 0,
                "damaged": 0,
                "blocked": 0,
                "version": 0,
                "updated_at": now,
            }

        inventory = self.inventory_store[key]
        inventory["on_hand"] += data.quantity
        inventory["version"] += 1
        inventory["updated_at"] = now

        ledger_record = {
            "id": str(uuid4()),
            "store_id": data.store_id,
            "sku_id": data.sku_id,
            "movement_type": "RECEIPT",
            "quantity": data.quantity,
            "reference_id": data.reference_id,
            "idempotency_key": data.idempotency_key,
            "created_at": now,
        }

        self.ledger_store[data.idempotency_key] = ledger_record
        return inventory

    async def adjust(
        self,
        data: StockAdjustment,
    ) -> dict:

        if data.idempotency_key in self.ledger_store:
            return self.ledger_store[data.idempotency_key]

        key = f"{data.store_id}:{data.sku_id}"
        if key not in self.inventory_store:
            raise ValueError("Inventory not found")

        inventory = self.inventory_store[key]
        new_val = inventory["on_hand"] + data.delta
        min_req = inventory["reserved"] + inventory["damaged"] + inventory["blocked"]

        if new_val < min_req:
            raise ValueError("Adjustment would violate inventory invariants")

        inventory["on_hand"] = new_val
        inventory["version"] += 1
        inventory["updated_at"] = datetime.now(timezone.utc)

        ledger_record = {
            "id": str(uuid4()),
            "store_id": data.store_id,
            "sku_id": data.sku_id,
            "movement_type": "ADJUSTMENT",
            "quantity": data.delta,
            "reference_id": data.reason,
            "idempotency_key": data.idempotency_key,
            "created_at": inventory["updated_at"],
        }

        self.ledger_store[data.idempotency_key] = ledger_record
        return inventory
