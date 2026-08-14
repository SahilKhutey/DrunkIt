"""Delivery domain service."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from faccp_platform.events.envelope import EventEnvelope, EventMetadata
from faccp_platform.events.outbox import OutboxService
from faccp_platform.events.topics import Topics

from ..domain.enums import DeliveryStatus, VerificationStatus
from ..domain.events import DeliveryAssignedEvent, DeliveryDeliveredEvent
from ..domain.state_machine import transition_delivery
from ..models.delivery import Delivery
from ..models.verification import DeliveryVerification
from ..repositories.delivery import DeliveryRepository
from .assignment import DeliveryAssignmentService


class DeliveryService:
    """Service managing last-mile delivery assignment, transitions, verification handoffs, and completion."""

    def __init__(
        self,
        session: AsyncSession,
        assignment_service: DeliveryAssignmentService | None = None,
    ) -> None:
        self.session = session
        self.repository = DeliveryRepository(session)
        self.assignment = assignment_service or DeliveryAssignmentService()

    async def get(self, delivery_id: str | uuid.UUID) -> Delivery | None:
        """Fetch delivery record by ID."""
        return await self.repository.get(delivery_id)

    async def create_delivery(
        self, order_id: str | uuid.UUID, fulfillment_id: str | uuid.UUID
    ) -> Delivery:
        """Create new delivery record."""
        delivery = Delivery(
            order_id=str(order_id),
            fulfillment_id=str(fulfillment_id),
            status=DeliveryStatus.CREATED,
        )
        self.session.add(delivery)
        await self.session.flush()
        return delivery

    async def assign_courier(self, delivery: Delivery) -> Delivery:
        """Assign best active courier to delivery."""
        couriers = await self.repository.get_active_couriers()
        transition_delivery(delivery.status, DeliveryStatus.ASSIGNING)
        delivery.status = DeliveryStatus.ASSIGNING
        await self.assignment.assign(delivery, couriers)
        await self.session.flush()

        # Outbox Event
        if self.session is not None:
            outbox = OutboxService(self.session)
            evt = DeliveryAssignedEvent(
                delivery_id=delivery.id,
                order_id=delivery.order_id,
                courier_id=delivery.courier_id or "",
            )
            env = EventEnvelope(
                event_type=evt.event_type,
                metadata=EventMetadata(producer="delivery-service"),
                payload=evt.payload(),
            )
            await outbox.enqueue(topic=Topics.DELIVERY_EVENTS, event=env)

        return delivery

    async def pickup(self, delivery: Delivery) -> Delivery:
        """Mark courier pickup and transition to IN_TRANSIT."""
        transition_delivery(delivery.status, DeliveryStatus.PICKED_UP)
        delivery.status = DeliveryStatus.PICKED_UP
        transition_delivery(delivery.status, DeliveryStatus.IN_TRANSIT)
        delivery.status = DeliveryStatus.IN_TRANSIT
        await self.session.flush()
        return delivery

    async def arrived(self, delivery: Delivery) -> Delivery:
        """Mark courier arrival at customer address and transition to VERIFICATION_PENDING."""
        transition_delivery(delivery.status, DeliveryStatus.ARRIVED)
        delivery.status = DeliveryStatus.ARRIVED
        transition_delivery(delivery.status, DeliveryStatus.VERIFICATION_PENDING)
        delivery.status = DeliveryStatus.VERIFICATION_PENDING
        await self.session.flush()
        return delivery

    async def complete_delivery(
        self, delivery: Delivery, verification: DeliveryVerification
    ) -> Delivery:
        """Complete delivery if verification passed."""
        if delivery.status != DeliveryStatus.VERIFICATION_PENDING:
            raise ValueError("Delivery is not awaiting verification")
        if verification.status != VerificationStatus.PASSED:
            raise ValueError("Delivery verification failed")

        transition_delivery(delivery.status, DeliveryStatus.DELIVERED)
        delivery.status = DeliveryStatus.DELIVERED
        delivery.delivered_at = datetime.now(timezone.utc)
        await self.session.flush()

        # Outbox Event
        if self.session is not None:
            outbox = OutboxService(self.session)
            evt = DeliveryDeliveredEvent(
                delivery_id=delivery.id,
                order_id=delivery.order_id,
                delivered_at=delivery.delivered_at.isoformat(),
            )
            env = EventEnvelope(
                event_type=evt.event_type,
                metadata=EventMetadata(producer="delivery-service"),
                payload=evt.payload(),
            )
            await outbox.enqueue(topic=Topics.DELIVERY_EVENTS, event=env)

        return delivery

    async def fail_delivery(self, delivery: Delivery) -> Delivery:
        """Transition delivery to RETURNING state on verification or handoff failure."""
        transition_delivery(delivery.status, DeliveryStatus.RETURNING)
        delivery.status = DeliveryStatus.RETURNING
        await self.session.flush()
        return delivery
