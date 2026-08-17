"""Consumer Verification domain service (privacy-preserving)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from faccp_platform.events.envelope import EventEnvelope, EventMetadata
from faccp_platform.events.outbox import OutboxService
from faccp_platform.events.topics import Topics

from ..domain.enums import VerificationMethod, VerificationStatus
from ..domain.events import ConsumerVerificationCompletedEvent
from ..models.verification import ConsumerVerification
from ..repositories.verification import VerificationRepository


class VerificationService:
    """Business service managing consumer verification states."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = VerificationRepository(session)

    async def get(self, consumer_id: str | uuid.UUID) -> ConsumerVerification | None:
        """Fetch verification status for consumer."""
        return await self.repository.get(consumer_id)

    async def mark_verified(
        self,
        consumer_id: str | uuid.UUID,
        *,
        method: VerificationMethod,
        provider_reference: str | None = None,
        verified_at: datetime | None = None,
        expires_at: datetime | None = None,
    ) -> ConsumerVerification:
        """Mark consumer verification status as verified and record event in Outbox."""
        verification = await self.repository.mark_verified(
            consumer_id,
            method=method,
            provider_reference=provider_reference,
            verified_at=verified_at,
            expires_at=expires_at,
        )

        # Enqueue ConsumerVerificationCompletedEvent in Outbox
        if self.session is not None:
            outbox = OutboxService(self.session)
            verified_event = ConsumerVerificationCompletedEvent(
                consumer_id=str(consumer_id),
                verification_status=verification.status.value,
                verification_method=method.value,
            )
            envelope = EventEnvelope(
                event_type=verified_event.event_type,
                metadata=EventMetadata(producer="consumer-service"),
                payload=verified_event.payload(),
            )
            await outbox.enqueue(topic=Topics.IDENTITY_EVENTS, event=envelope)

        return verification
