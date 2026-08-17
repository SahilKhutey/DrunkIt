"""Cart domain service."""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.cart import Cart
from ..models.cart_item import CartItem
from ..repositories.cart import CartRepository


class CartService:
    """Service managing shopping cart operations."""

    def __init__(self, session: AsyncSession | None = None) -> None:
        self.session = session
        self.repository = CartRepository(session) if session is not None else None
        self.carts: dict[str, dict] = {}
        self.cart_items: dict[str, list[dict]] = {}

    async def create_cart(self, consumer_id: str | uuid.UUID) -> Cart:
        """Create new cart."""
        if self.repository is None:
            cid = str(uuid.uuid4())
            cart_obj = Cart(id=cid, consumer_id=str(consumer_id))
            self.carts[cid] = {"id": cid, "customer_id": str(consumer_id)}
            return cart_obj
        return await self.repository.create(consumer_id)

    async def get_or_create_cart(self, customer_id: str, store_id: str = "") -> dict[str, Any]:
        """Legacy helper for cart retrieval."""
        cid = f"cart_{customer_id}"
        cart = {"id": cid, "customer_id": customer_id, "store_id": store_id, "items": []}
        self.carts[cid] = cart
        return cart

    async def add_item(
        self,
        cart_id: str | uuid.UUID,
        product_id: str | uuid.UUID | None = None,
        quantity: Decimal | int = Decimal("1"),
        unit_price: Decimal = Decimal("0"),
        sku_id: str | None = None,
    ) -> Any:
        """Add item to cart."""
        cid = str(cart_id)
        sku = sku_id or (str(product_id) if product_id else str(uuid.uuid4()))
        item_dict = {"cart_id": cid, "sku_id": sku, "product_id": sku, "quantity": quantity, "unit_price": unit_price}
        if cid not in self.cart_items:
            self.cart_items[cid] = []
        self.cart_items[cid].append(item_dict)

        if self.repository is None:
            return item_dict

        qty = Decimal(str(quantity))
        item = CartItem(
            cart_id=cid,
            product_id=sku,
            quantity=qty,
            unit_price=unit_price,
        )
        self.session.add(item)
        await self.session.flush()
        return item
