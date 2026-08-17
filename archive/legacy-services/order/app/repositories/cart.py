"""Cart repository."""

from __future__ import annotations

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.cart import Cart
from ..models.cart_item import CartItem


class CartRepository:
    """Repository handling cart operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, cart_id: str | uuid.UUID) -> Cart | None:
        """Fetch cart by ID."""
        cid_str = str(cart_id)
        result = await self.session.execute(select(Cart).where(Cart.id == cid_str))
        return result.scalar_one_or_none()

    async def create(self, consumer_id: str | uuid.UUID) -> Cart:
        """Create a new cart for consumer."""
        cid_str = str(consumer_id)
        cart = Cart(consumer_id=cid_str)
        self.session.add(cart)
        await self.session.flush()
        return cart

    async def get_items(self, cart_id: str | uuid.UUID) -> list[CartItem]:
        """Fetch all items in cart."""
        cid_str = str(cart_id)
        result = await self.session.execute(
            select(CartItem).where(CartItem.cart_id == cid_str)
        )
        return list(result.scalars().all())
