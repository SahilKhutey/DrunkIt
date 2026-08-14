"""Fulfillment repository."""

from __future__ import annotations

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.fulfillment import Fulfillment


class FulfillmentRepository:
    """Repository handling fulfillment persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, fulfillment_id: str | uuid.UUID) -> Fulfillment | None:
        """Fetch fulfillment by ID."""
        fid_str = str(fulfillment_id)
        result = await self.session.execute(select(Fulfillment).where(Fulfillment.id == fid_str))
        return result.scalar_one_or_none()

    async def get_by_order(self, order_id: str | uuid.UUID) -> Fulfillment | None:
        """Fetch fulfillment by order_id."""
        oid_str = str(order_id)
        result = await self.session.execute(select(Fulfillment).where(Fulfillment.order_id == oid_str))
        return result.scalar_one_or_none()
