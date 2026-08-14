"""Order repository."""

from __future__ import annotations

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.order import Order
from ..models.order_item import OrderItem


class OrderRepository:
    """Repository handling order persistence and idempotency key resolution."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, order_id: str | uuid.UUID) -> Order | None:
        """Fetch order by ID."""
        oid_str = str(order_id)
        result = await self.session.execute(select(Order).where(Order.id == oid_str))
        return result.scalar_one_or_none()

    async def get_by_idempotency(self, consumer_id: str | uuid.UUID, idempotency_key: str) -> Order | None:
        """Fetch existing order by consumer_id and idempotency_key."""
        cid_str = str(consumer_id)
        stmt = select(Order).where(
            Order.consumer_id == cid_str,
            Order.idempotency_key == idempotency_key,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_items(self, order_id: str | uuid.UUID) -> list[OrderItem]:
        """Fetch order items for order_id."""
        oid_str = str(order_id)
        result = await self.session.execute(
            select(OrderItem).where(OrderItem.order_id == oid_str)
        )
        return list(result.scalars().all())
