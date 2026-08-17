"""Inventory domain service."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.reservation import InventoryReservation
from ..repositories.inventory import InventoryRepository


class InventoryService:
    """Service handling atomic inventory reservation and TTL expiration cleanup."""

    RESERVATION_TTL_MINUTES = 15

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = InventoryRepository(session)

    async def reserve(
        self,
        order_id: str | uuid.UUID,
        product_id: str | uuid.UUID,
        warehouse_id: str | uuid.UUID,
        quantity: int = 1,
    ) -> InventoryReservation:
        """Reserve stock atomically and create TTL reservation record."""
        await self.repository.get_or_create(product_id, warehouse_id, available_qty=100)
        await self.repository.reserve_inventory(product_id, warehouse_id, quantity)

        reservation = InventoryReservation(
            order_id=str(order_id),
            product_id=str(product_id),
            warehouse_id=str(warehouse_id),
            quantity=quantity,
            status="reserved",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=self.RESERVATION_TTL_MINUTES),
        )
        self.session.add(reservation)
        await self.session.flush()
        return reservation

    async def release_expired_reservations(self) -> int:
        """Find and release stock for all expired reservations."""
        now = datetime.now(timezone.utc)
        stmt = select(InventoryReservation).where(
            InventoryReservation.status == "reserved",
            InventoryReservation.expires_at < now,
        )
        res = await self.session.execute(stmt)
        reservations = res.scalars().all()
        count = 0
        for reservation in reservations:
            await self.repository.release_inventory(reservation)
            count += 1
        await self.session.flush()
        return count
