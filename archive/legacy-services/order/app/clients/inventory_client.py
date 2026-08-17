class InventoryClient:

    def __init__(self, http=None):
        self.http = http

    async def reserve(
        self,
        order_id: str,
        store_id: str,
        sku_id: str,
        quantity: int,
        idempotency_key: str,
    ) -> dict:

        if sku_id == "out-of-stock":
            raise ValueError("INSUFFICIENT_STOCK")

        return {
            "status": "RESERVED",
            "order_id": order_id,
            "store_id": store_id,
            "sku_id": sku_id,
            "quantity": quantity,
        }
