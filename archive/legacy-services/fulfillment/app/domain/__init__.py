"""Fulfillment domain package."""

from .enums import DeliveryStatus, FulfillmentStatus, VerificationStatus
from .events import (
    DeliveryAssignedEvent,
    DeliveryDeliveredEvent,
    FulfillmentReadyEvent,
    InventoryReservedEvent,
    VerificationCompletedEvent,
)
from .state_machine import (
    DELIVERY_TRANSITIONS,
    FULFILLMENT_TRANSITIONS,
    transition_delivery,
    transition_fulfillment,
)

__all__ = [
    "DELIVERY_TRANSITIONS",
    "FULFILLMENT_TRANSITIONS",
    "DeliveryAssignedEvent",
    "DeliveryDeliveredEvent",
    "DeliveryStatus",
    "FulfillmentReadyEvent",
    "FulfillmentStatus",
    "InventoryReservedEvent",
    "VerificationCompletedEvent",
    "VerificationStatus",
    "transition_delivery",
    "transition_fulfillment",
]
