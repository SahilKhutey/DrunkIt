"""Fulfillment domain service."""

from __future__ import annotations

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from faccp_platform.events.envelope import EventEnvelope, EventMetadata
from faccp_platform.events.outbox import OutboxService
from faccp_platform.events.topics import Topics

from ..domain.enums import FulfillmentStatus
from ..domain.events import FulfillmentReadyEvent
from ..domain.state_machine import transition_fulfillment
from ..models.fulfillment import Fulfillment
from ..repositories.fulfillment import FulfillmentRepository
from .inventory_service import InventoryService


class FulfillmentService:
    """Service managing warehouse fulfillment picking, packing, and ready state operations."""

    def __init__(
        self,
        session: AsyncSession,
        inventory_service: InventoryService | None = None,
    ) -> None:
        self.session = session
        self.inventory = inventory_service or InventoryService(session)
        self.repository = FulfillmentRepository(session)

    async def get(self, fulfillment_id: str | uuid.UUID) -> Fulfillment | None:
        """Fetch fulfillment record."""
        return await self.repository.get(fulfillment_id)

    async def create_fulfillment(
        self,
        order_id: str | uuid.UUID,
        warehouse_id: str | uuid.UUID,
        product_id: str | uuid.UUID,
        quantity: int = 1,
    ) -> Fulfillment:
        """Create fulfillment and reserve inventory."""
        oid_str = str(order_id)
        wid_str = str(warehouse_id)
        pid_str = str(product_id)

        fulfillment = Fulfillment(
            order_id=oid_str,
            warehouse_id=wid_str,
            status=FulfillmentStatus.RESERVING,
        )
        self.session.add(fulfillment)

        # Reserve inventory
        await self.inventory.reserve(oid_str, pid_str, wid_str, quantity)

        fulfillment.status = FulfillmentStatus.RESERVED
        await self.session.flush()
        return fulfillment

    async def start_picking(self, fulfillment: Fulfillment) -> Fulfillment:
        """Transition fulfillment state to PICKING."""
        transition_fulfillment(fulfillment.status, FulfillmentStatus.PICKING)
        fulfillment.status = FulfillmentStatus.PICKING
        await self.session.flush()
        return fulfillment

    async def pack(self, fulfillment: Fulfillment) -> Fulfillment:
        """Transition fulfillment state to PACKING."""
        transition_fulfillment(fulfillment.status, FulfillmentStatus.PACKING)
        fulfillment.status = FulfillmentStatus.PACKING
        await self.session.flush()
        return fulfillment

    async def mark_ready(self, fulfillment: Fulfillment) -> Fulfillment:
        """Transition fulfillment state to READY_FOR_PICKUP."""
        transition_fulfillment(fulfillment.status, FulfillmentStatus.READY_FOR_PICKUP)
        fulfillment.status = FulfillmentStatus.READY_FOR_PICKUP
        await self.session.flush()

        # Outbox Event
        if self.session is not None:
            outbox = OutboxService(self.session)
            evt = FulfillmentReadyEvent(
                fulfillment_id=fulfillment.id,
                order_id=fulfillment.order_id,
                warehouse_id=fulfillment.warehouse_id,
            )
            env = EventEnvelope(
                event_type=evt.event_type,
                metadata=EventMetadata(producer="fulfillment-service"),
                payload=evt.payload(),
            )
            await outbox.enqueue(topic=Topics.FULFILLMENT_EVENTS, event=env)

        return fulfillment
