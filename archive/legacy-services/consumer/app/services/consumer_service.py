"""Consumer business domain service."""

from __future__ import annotations

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from faccp_platform.events.envelope import EventEnvelope, EventMetadata
from faccp_platform.events.outbox import OutboxService
from faccp_platform.events.topics import Topics

from ..domain.enums import ConsumerStatus
from ..domain.errors import ConsumerAlreadyExistsError, ConsumerNotFoundError, InvalidStateTransitionError
from ..domain.events import ConsumerActivatedEvent, ConsumerCreatedEvent
from ..models.consumer import Consumer
from ..repositories.consumer import ConsumerRepository


class ConsumerService:
    """Business service managing Consumer aggregate root lifecycles."""

    def __init__(self, repository: ConsumerRepository, session: AsyncSession | None = None) -> None:
        self.repository = repository
        self.session = session or getattr(repository, "session", None)

    async def create(self, identity_id: str | uuid.UUID) -> Consumer:
        """Create a new Consumer record and enqueue ConsumerCreatedEvent into Outbox."""
        iid_str = str(identity_id)
        existing = await self.repository.get_by_identity(iid_str)
        if existing:
            raise ValueError("Consumer already exists")

        consumer = await self.repository.create(iid_str)

        # Transactional outbox event enqueue
        if self.session is not None:
            outbox = OutboxService(self.session)
            created_event = ConsumerCreatedEvent(
                consumer_id=str(consumer.id),
                identity_id=str(consumer.identity_id),
            )
            envelope = EventEnvelope(
                event_type=created_event.event_type,
                metadata=EventMetadata(producer="consumer-service"),
                payload=created_event.payload(),
            )
            await outbox.enqueue(topic=Topics.IDENTITY_EVENTS, event=envelope)

        return consumer

    async def get(self, consumer_id: str | uuid.UUID) -> Consumer | None:
        """Fetch consumer by ID."""
        return await self.repository.get(consumer_id)

    async def activate(self, consumer_id: str | uuid.UUID) -> Consumer:
        """Activate consumer status."""
        consumer = await self.repository.get(consumer_id)
        if consumer is None:
            raise ConsumerNotFoundError("Consumer not found")

        if consumer.status == ConsumerStatus.DEACTIVATED:
            raise InvalidStateTransitionError("Cannot activate deactivated consumer")

        consumer.status = ConsumerStatus.ACTIVE
        consumer.version += 1
        await self.session.flush()

        # Enqueue ConsumerActivatedEvent into Outbox
        if self.session is not None:
            outbox = OutboxService(self.session)
            activated_event = ConsumerActivatedEvent(consumer_id=str(consumer.id))
            envelope = EventEnvelope(
                event_type=activated_event.event_type,
                metadata=EventMetadata(producer="consumer-service"),
                payload=activated_event.payload(),
            )
            await outbox.enqueue(topic=Topics.IDENTITY_EVENTS, event=envelope)

        return consumer
