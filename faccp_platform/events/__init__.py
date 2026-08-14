"""Platform Event Kernel package."""

from .contracts import (
    DomainEvent,
    InventoryReservationFailedEvent,
    InventoryReservedEvent,
    OrderCreatedEvent,
    PaymentAuthorizedEvent,
    PaymentFailedEvent,
)
from .consumer import EventConsumer, EventHandler
from .dlq import DeadLetterPublisher
from .envelope import EventEnvelope, EventMetadata
from .exceptions import (
    EventConsumeError,
    EventError,
    EventIdempotencyError,
    EventPublishError,
)
from .idempotency import EventIdempotency
from .outbox import OutboxService
from .producer import EventProducer
from .registry import EVENT_TYPES, get_event_contract
from .retry import RetryPolicy
from .serialization import deserialize_event, serialize_event
from .topics import Topics

__all__ = [
    "DeadLetterPublisher",
    "DomainEvent",
    "EVENT_TYPES",
    "EventConsumeError",
    "EventConsumer",
    "EventEnvelope",
    "EventError",
    "EventHandler",
    "EventIdempotency",
    "EventIdempotencyError",
    "EventMetadata",
    "EventProducer",
    "EventPublishError",
    "InventoryReservationFailedEvent",
    "InventoryReservedEvent",
    "OrderCreatedEvent",
    "OutboxService",
    "PaymentAuthorizedEvent",
    "PaymentFailedEvent",
    "RetryPolicy",
    "Topics",
    "deserialize_event",
    "get_event_contract",
    "serialize_event",
]
