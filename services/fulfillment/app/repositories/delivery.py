"""Delivery repository."""

from __future__ import annotations

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.courier import Courier
from ..models.delivery import Delivery
from ..models.verification import DeliveryVerification


class DeliveryRepository:
    """Repository handling delivery, courier, and verification persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, delivery_id: str | uuid.UUID) -> Delivery | None:
        """Fetch delivery by ID."""
        did_str = str(delivery_id)
        result = await self.session.execute(select(Delivery).where(Delivery.id == did_str))
        return result.scalar_one_or_none()

    async def get_by_order(self, order_id: str | uuid.UUID) -> Delivery | None:
        """Fetch delivery by order_id."""
        oid_str = str(order_id)
        result = await self.session.execute(select(Delivery).where(Delivery.order_id == oid_str))
        return result.scalar_one_or_none()

    async def get_active_couriers(self) -> list[Courier]:
        """Fetch all active couriers."""
        result = await self.session.execute(select(Courier).where(Courier.active == True))
        return list(result.scalars().all())

    async def get_verification(self, verification_id: str | uuid.UUID) -> DeliveryVerification | None:
        """Fetch delivery verification by ID."""
        vid_str = str(verification_id)
        result = await self.session.execute(select(DeliveryVerification).where(DeliveryVerification.id == vid_str))
        return result.scalar_one_or_none()

    async def get_verification_by_delivery(self, delivery_id: str | uuid.UUID) -> DeliveryVerification | None:
        """Fetch verification record for a delivery."""
        did_str = str(delivery_id)
        result = await self.session.execute(select(DeliveryVerification).where(DeliveryVerification.delivery_id == did_str))
        return result.scalar_one_or_none()
