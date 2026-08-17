"""Delivery verification service."""

from __future__ import annotations

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from faccp_platform.events.envelope import EventEnvelope, EventMetadata
from faccp_platform.events.outbox import OutboxService
from faccp_platform.events.topics import Topics

from ..domain.enums import VerificationStatus
from ..domain.events import VerificationCompletedEvent
from ..models.verification import DeliveryVerification
from ..repositories.delivery import DeliveryRepository


class VerificationService:
    """Service managing customer age/identity handoff verification."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = DeliveryRepository(session)

    async def get(self, verification_id: str | uuid.UUID) -> DeliveryVerification | None:
        """Fetch verification record by ID."""
        return await self.repository.get_verification(verification_id)

    async def get_by_delivery(self, delivery_id: str | uuid.UUID) -> DeliveryVerification | None:
        """Fetch verification record by delivery_id."""
        return await self.repository.get_verification_by_delivery(delivery_id)

    async def start(self, delivery_id: str | uuid.UUID) -> DeliveryVerification:
        """Start pending verification for a delivery."""
        did_str = str(delivery_id)
        existing = await self.repository.get_verification_by_delivery(did_str)
        if existing:
            return existing

        verification = DeliveryVerification(
            delivery_id=did_str,
            status=VerificationStatus.PENDING,
        )
        self.session.add(verification)
        await self.session.flush()
        return verification

    async def complete(
        self,
        verification: DeliveryVerification,
        *,
        passed: bool,
        method: str,
        reference: str,
    ) -> DeliveryVerification:
        """Complete verification with pass or fail status."""
        if verification.status != VerificationStatus.PENDING:
            raise ValueError("Verification is not pending")

        verification.verification_method = method
        verification.verification_reference = reference
        verification.status = VerificationStatus.PASSED if passed else VerificationStatus.FAILED
        await self.session.flush()

        # Outbox Event
        if self.session is not None:
            outbox = OutboxService(self.session)
            evt = VerificationCompletedEvent(
                verification_id=verification.id,
                delivery_id=verification.delivery_id,
                status=verification.status,
                method=method,
            )
            env = EventEnvelope(
                event_type=evt.event_type,
                metadata=EventMetadata(producer="fulfillment-service-verification"),
                payload=evt.payload(),
            )
            await outbox.enqueue(topic=Topics.DELIVERY_EVENTS, event=env)

        return verification
