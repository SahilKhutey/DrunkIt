"""Inventory repository."""

from __future__ import annotations

import uuid
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.inventory import Inventory
from ..models.reservation import InventoryReservation


class InventoryRepository:
    """Repository handling inventory and reservation persistence with atomic SQL updates."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_create(self, product_id: str | uuid.UUID, warehouse_id: str | uuid.UUID, available_qty: int = 100) -> Inventory:
        """Fetch existing inventory or initialize new inventory record."""
        pid_str = str(product_id)
        wid_str = str(warehouse_id)
        stmt = select(Inventory).where(
            Inventory.product_id == pid_str,
            Inventory.warehouse_id == wid_str,
        )
        res = await self.session.execute(stmt)
        inv = res.scalar_one_or_none()
        if not inv:
            inv = Inventory(product_id=pid_str, warehouse_id=wid_str, available_quantity=available_qty)
            self.session.add(inv)
            await self.session.flush()
        return inv

    async def reserve_inventory(
        self, product_id: str | uuid.UUID, warehouse_id: str | uuid.UUID, quantity: int
    ) -> None:
        """Execute atomic conditional SQL update to reserve inventory without race conditions."""
        pid_str = str(product_id)
        wid_str = str(warehouse_id)
        stmt = (
            update(Inventory)
            .where(
                Inventory.product_id == pid_str,
                Inventory.warehouse_id == wid_str,
                Inventory.available_quantity >= quantity,
            )
            .values(
                available_quantity=Inventory.available_quantity - quantity,
                reserved_quantity=Inventory.reserved_quantity + quantity,
            )
        )
        res = await self.session.execute(stmt)
        if res.rowcount != 1:
            raise ValueError("Insufficient inventory")

    async def release_inventory(
        self, reservation: InventoryReservation
    ) -> None:
        """Release reserved inventory back to available stock."""
        stmt = (
            update(Inventory)
            .where(
                Inventory.product_id == str(reservation.product_id),
                Inventory.warehouse_id == str(reservation.warehouse_id),
            )
            .values(
                available_quantity=Inventory.available_quantity + reservation.quantity,
                reserved_quantity=Inventory.reserved_quantity - reservation.quantity,
            )
        )
        await self.session.execute(stmt)
        reservation.status = "expired"
