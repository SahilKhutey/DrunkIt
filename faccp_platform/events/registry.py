"""Event registry mapping event types to strongly-typed contracts."""

from __future__ import annotations

from typing import Type
from .contracts import (
    AccessDeniedEvent,
    ConsumerActivatedEvent,
    ConsumerCreatedEvent,
    ConsumerVerificationCompletedEvent,
    DeliveryAssignedEvent,
    DeliveryDeliveredEvent,
    DomainEvent,
    EligibilityEvaluatedEvent,
    FulfillmentReadyEvent,
    InventoryReservationFailedEvent,
    InventoryReservedEvent,
    LoginFailedEvent,
    LoginSucceededEvent,
    OrderCreatedEvent,
    PaymentAuthorizedEvent,
    PaymentCapturedEvent,
    PaymentCreatedEvent,
    PaymentFailedEvent,
    RiskEvaluatedEvent,
    VerificationCompletedEvent,
)

EVENT_TYPES: dict[str, Type[DomainEvent]] = {
    OrderCreatedEvent.event_type: OrderCreatedEvent,
    PaymentAuthorizedEvent.event_type: PaymentAuthorizedEvent,
    PaymentCreatedEvent.event_type: PaymentCreatedEvent,
    PaymentCapturedEvent.event_type: PaymentCapturedEvent,
    PaymentFailedEvent.event_type: PaymentFailedEvent,
    RiskEvaluatedEvent.event_type: RiskEvaluatedEvent,
    InventoryReservedEvent.event_type: InventoryReservedEvent,
    InventoryReservationFailedEvent.event_type: InventoryReservationFailedEvent,
    FulfillmentReadyEvent.event_type: FulfillmentReadyEvent,
    DeliveryAssignedEvent.event_type: DeliveryAssignedEvent,
    DeliveryDeliveredEvent.event_type: DeliveryDeliveredEvent,
    VerificationCompletedEvent.event_type: VerificationCompletedEvent,
    LoginSucceededEvent.event_type: LoginSucceededEvent,
    LoginFailedEvent.event_type: LoginFailedEvent,
    AccessDeniedEvent.event_type: AccessDeniedEvent,
    ConsumerCreatedEvent.event_type: ConsumerCreatedEvent,
    ConsumerActivatedEvent.event_type: ConsumerActivatedEvent,
    ConsumerVerificationCompletedEvent.event_type: ConsumerVerificationCompletedEvent,
    EligibilityEvaluatedEvent.event_type: EligibilityEvaluatedEvent,
}


def get_event_contract(event_type: str) -> Type[DomainEvent]:
    """Retrieve contract class for a registered event type."""
    try:
        return EVENT_TYPES[event_type]
    except KeyError as exc:
        raise ValueError(f"Unknown event type: {event_type}") from exc
