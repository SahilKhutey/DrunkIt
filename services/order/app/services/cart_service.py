from datetime import datetime, timezone
from uuid import uuid4


class CartService:

    def __init__(self):
        self.carts: dict[str, dict] = {}
        self.cart_items: dict[str, list[dict]] = {}

    async def get_or_create_cart(self, customer_id: str, store_id: str | None = None) -> dict:
        for cart in self.carts.values():
            if cart["customer_id"] == customer_id and cart["status"] == "ACTIVE":
                return cart

        cart_id = str(uuid4())
        now = datetime.now(timezone.utc)
        cart = {
            "id": cart_id,
            "customer_id": customer_id,
            "store_id": store_id,
            "status": "ACTIVE",
            "created_at": now,
            "updated_at": now,
        }
        self.carts[cart_id] = cart
        self.cart_items[cart_id] = []
        return cart

    async def add_item(self, cart_id: str, sku_id: str, quantity: int) -> dict:
        items = self.cart_items.setdefault(cart_id, [])
        for item in items:
            if item["sku_id"] == sku_id:
                item["quantity"] += quantity
                return item

        item = {
            "id": str(uuid4()),
            "cart_id": cart_id,
            "sku_id": sku_id,
            "quantity": quantity,
        }
        items.append(item)
        return item

    async def update_item(self, cart_id: str, sku_id: str, quantity: int) -> dict:
        items = self.cart_items.get(cart_id, [])
        for item in items:
            if item["sku_id"] == sku_id:
                item["quantity"] = quantity
                return item
        raise ValueError("ITEM_NOT_IN_CART")
