from services.inventory.app.services.inventory_service import InventoryService


class ReconciliationService:

    def __init__(self, inventory_service: InventoryService):
        self.inventory_service = inventory_service

    async def reconcile(
        self,
        store_id: str,
        sku_id: str,
    ) -> dict:

        # Sum ledger movements
        ledger_stock = 0
        for entry in self.inventory_service.ledger_store.values():
            if entry["store_id"] == store_id and entry["sku_id"] == sku_id:
                if entry["movement_type"] in ("RECEIPT", "ADJUSTMENT", "RETURN"):
                    ledger_stock += entry["quantity"]
                elif entry["movement_type"] in ("SALE", "DAMAGE"):
                    ledger_stock -= entry["quantity"]

        key = f"{store_id}:{sku_id}"
        inventory = self.inventory_service.inventory_store.get(key)
        if not inventory:
            raise ValueError("Inventory missing")

        inventory_stock = inventory["on_hand"]
        difference = ledger_stock - inventory_stock

        return {
            "store_id": store_id,
            "sku_id": sku_id,
            "ledger_stock": ledger_stock,
            "inventory_stock": inventory_stock,
            "difference": difference,
            "consistent": (difference == 0),
        }
