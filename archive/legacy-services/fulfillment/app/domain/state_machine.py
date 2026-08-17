"""Fulfillment and Delivery state machine transition rules."""

from __future__ import annotations

from typing import Any
from .enums import DeliveryStatus, FulfillmentStatus

FULFILLMENT_TRANSITIONS: dict[FulfillmentStatus, set[FulfillmentStatus]] = {
    FulfillmentStatus.CREATED: {
        FulfillmentStatus.RESERVING,
        FulfillmentStatus.CANCELLED,
    },
    FulfillmentStatus.RESERVING: {
        FulfillmentStatus.RESERVED,
        FulfillmentStatus.FAILED,
    },
    FulfillmentStatus.RESERVED: {
        FulfillmentStatus.PICKING,
        FulfillmentStatus.CANCELLED,
    },
    FulfillmentStatus.PICKING: {
        FulfillmentStatus.PACKING,
        FulfillmentStatus.FAILED,
    },
    FulfillmentStatus.PACKING: {
        FulfillmentStatus.READY_FOR_PICKUP,
        FulfillmentStatus.FAILED,
    },
    FulfillmentStatus.READY_FOR_PICKUP: {
        FulfillmentStatus.HANDED_TO_CARRIER,
        FulfillmentStatus.CANCELLED,
    },
    FulfillmentStatus.HANDED_TO_CARRIER: {
        FulfillmentStatus.COMPLETED,
        FulfillmentStatus.FAILED,
    },
    FulfillmentStatus.COMPLETED: set(),
    FulfillmentStatus.FAILED: set(),
    FulfillmentStatus.CANCELLED: set(),
}

DELIVERY_TRANSITIONS: dict[DeliveryStatus, set[DeliveryStatus]] = {
    DeliveryStatus.CREATED: {
        DeliveryStatus.ASSIGNING,
        DeliveryStatus.FAILED,
    },
    DeliveryStatus.ASSIGNING: {
        DeliveryStatus.ASSIGNED,
        DeliveryStatus.FAILED,
    },
    DeliveryStatus.ASSIGNED: {
        DeliveryStatus.PICKED_UP,
        DeliveryStatus.FAILED,
    },
    DeliveryStatus.PICKED_UP: {
        DeliveryStatus.IN_TRANSIT,
    },
    DeliveryStatus.IN_TRANSIT: {
        DeliveryStatus.ARRIVED,
        DeliveryStatus.FAILED,
    },
    DeliveryStatus.ARRIVED: {
        DeliveryStatus.VERIFICATION_PENDING,
    },
    DeliveryStatus.VERIFICATION_PENDING: {
        DeliveryStatus.DELIVERED,
        DeliveryStatus.RETURNING,
    },
    DeliveryStatus.DELIVERED: set(),
    DeliveryStatus.RETURNING: {
        DeliveryStatus.RETURNED,
    },
    DeliveryStatus.RETURNED: set(),
    DeliveryStatus.FAILED: set(),
}


def transition_fulfillment(current: FulfillmentStatus, target: FulfillmentStatus) -> FulfillmentStatus:
    """Validate and return target fulfillment status or raise ValueError."""
    allowed = FULFILLMENT_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise ValueError(f"Invalid fulfillment transition: {current} -> {target}")
    return target


def transition_delivery(current: DeliveryStatus, target: DeliveryStatus) -> DeliveryStatus:
    """Validate and return target delivery status or raise ValueError."""
    allowed = DELIVERY_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise ValueError(f"Invalid delivery transition: {current} -> {target}")
    return target
