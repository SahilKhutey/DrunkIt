from app.schemas.inventory import (
    InventoryItem,
)


class InventoryService:

    def __init__(self):

        self._inventory = {

            ("STORE-001", "PROD-001"):
                InventoryItem(
                    product_id="PROD-001",
                    store_id="STORE-001",
                    quantity_available=20,
                    reserved_quantity=2,
                ),

            ("STORE-002", "PROD-001"):
                InventoryItem(
                    product_id="PROD-001",
                    store_id="STORE-002",
                    quantity_available=8,
                    reserved_quantity=1,
                ),
        }

    async def get_item(
        self,
        store_id: str,
        product_id: str,
    ):

        return self._inventory.get(
            (store_id, product_id)
        )

    async def has_quantity(
        self,
        store_id: str,
        product_id: str,
        quantity: int,
    ) -> bool:

        item = await self.get_item(
            store_id,
            product_id,
        )

        if item is None:
            return False

        return (
            item.sellable_quantity
            >= quantity
        )
