"""Inventory service: Stock Balance, TTL Reservations, Atomic Deductions & Audit Logs."""

from __future__ import annotations

import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.communication.envelope import create_envelope
from faccp_common.communication.producer import EventProducer
from faccp_common.exceptions import BadRequestError, ConflictError, NotFoundError
from faccp_common.logging import get_logger

from app.config import get_settings
from app.db.models import InventoryAuditLog, InventoryItem, InventoryReservation
from app.schemas.inventory import (
    DeductRequest, ReleaseRequest, ReservationRequest, StockUpdate,
)

logger = get_logger(__name__)
settings = get_settings()


class InventoryService:
    """Real-time inventory engine with reservation holds and stock auditing."""

    def __init__(self, db: AsyncSession, producer: EventProducer | None = None) -> None:
        self.db = db
        self.producer = producer

    # ============================================================
    # STOCK MANAGEMENT
    # ============================================================
    async def set_stock(self, payload: StockUpdate, actor_id: str = "sys_admin") -> InventoryItem:
        existing = await self._get_inventory_item(payload.store_id, payload.sku_id)
        if existing:
            existing.available_quantity += payload.quantity
            item = existing
        else:
            item = InventoryItem(
                store_id=payload.store_id,
                sku_id=payload.sku_id,
                available_quantity=payload.quantity,
                reserved_quantity=0,
                reorder_level=payload.reorder_level,
                is_active=True,
            )
            self.db.add(item)

        await self.db.flush()

        audit = InventoryAuditLog(
            store_id=item.store_id,
            sku_id=item.sku_id,
            action="RESTOCK",
            quantity_change=payload.quantity,
            resulting_balance=item.available_quantity,
            performed_by=actor_id,
        )
        self.db.add(audit)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def get_stock(self, store_id: str, sku_id: str) -> InventoryItem:
        item = await self._get_inventory_item(store_id, sku_id)
        if not item:
            raise NotFoundError(f"No inventory record for store {store_id} and SKU {sku_id}")
        return item

    # ============================================================
    # RESERVATION ENGINE
    # ============================================================
    async def reserve_stock(self, payload: ReservationRequest) -> InventoryReservation:
        item = await self.get_stock(payload.store_id, payload.sku_id)

        if item.available_quantity < payload.quantity:
            raise ConflictError(f"Insufficient stock available. Requested: {payload.quantity}, Available: {item.available_quantity}")

        # Deduct available, increment reserved
        item.available_quantity -= payload.quantity
        item.reserved_quantity += payload.quantity

        token = f"RES_{secrets.token_hex(16).upper()}"
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.reservation_ttl_minutes)

        res = InventoryReservation(
            reservation_token=token,
            store_id=payload.store_id,
            sku_id=payload.sku_id,
            quantity=payload.quantity,
            status="HELD",
            expires_at=expires_at,
        )
        self.db.add(res)
        await self.db.commit()
        await self.db.refresh(res)

        await self._publish("inventory.reserved", {
            "reservation_token": token, "store_id": payload.store_id,
            "sku_id": payload.sku_id, "quantity": payload.quantity,
        })
        return res

    async def release_reservation(self, payload: ReleaseRequest) -> InventoryReservation:
        res = await self._get_reservation(payload.reservation_token)
        if not res:
            raise NotFoundError(f"Reservation token {payload.reservation_token} not found")

        if res.status != "HELD":
            raise BadRequestError(f"Reservation is in status {res.status}, cannot release")

        item = await self.get_stock(res.store_id, res.sku_id)
        item.available_quantity += res.quantity
        item.reserved_quantity -= res.quantity

        res.status = "RELEASED"
        await self.db.commit()
        await self.db.refresh(res)

        await self._publish("inventory.released", {
            "reservation_token": res.reservation_token, "store_id": res.store_id, "sku_id": res.sku_id,
        })
        return res

    async def deduct_reservation(self, payload: DeductRequest) -> InventoryReservation:
        res = await self._get_reservation(payload.reservation_token)
        if not res:
            raise NotFoundError(f"Reservation token {payload.reservation_token} not found")

        if res.status != "HELD":
            raise BadRequestError(f"Reservation is in status {res.status}, cannot deduct")

        item = await self.get_stock(res.store_id, res.sku_id)
        item.reserved_quantity -= res.quantity

        res.status = "FULFILLED"

        audit = InventoryAuditLog(
            store_id=item.store_id,
            sku_id=item.sku_id,
            action="DEDUCT",
            quantity_change=-res.quantity,
            resulting_balance=item.available_quantity,
            performed_by="checkout_engine",
        )
        self.db.add(audit)
        await self.db.commit()
        await self.db.refresh(res)

        await self._publish("inventory.deducted", {
            "reservation_token": res.reservation_token, "store_id": res.store_id, "sku_id": res.sku_id,
        })
        return res

    # ============================================================
    # HELPERS
    # ============================================================
    async def _get_inventory_item(self, store_id: str, sku_id: str) -> InventoryItem | None:
        result = await self.db.execute(
            select(InventoryItem).where(InventoryItem.store_id == store_id, InventoryItem.sku_id == sku_id)
        )
        return result.scalar_one_or_none()

    async def _get_reservation(self, token: str) -> InventoryReservation | None:
        result = await self.db.execute(
            select(InventoryReservation).where(InventoryReservation.reservation_token == token)
        )
        return result.scalar_one_or_none()

    async def _publish(self, event_type: str, payload: dict) -> None:
        if not self.producer:
            return
        try:
            envelope = create_envelope(event_type, payload, producer="faccp-inventory")
            await self.producer.publish("inventory.events", envelope)
        except Exception:
            logger.exception("event_publish_failed", event_type=event_type)
