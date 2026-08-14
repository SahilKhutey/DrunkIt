"""Order state machine transition rules."""

from __future__ import annotations

from .enums import OrderStatus

TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.DRAFT: {
        OrderStatus.PENDING_COMPLIANCE,
        OrderStatus.CANCELLED,
    },
    OrderStatus.PENDING_COMPLIANCE: {
        OrderStatus.COMPLIANCE_FAILED,
        OrderStatus.PENDING_PAYMENT,
        OrderStatus.CANCELLED,
    },
    OrderStatus.COMPLIANCE_FAILED: {
        OrderStatus.CANCELLED,
    },
    OrderStatus.PENDING_PAYMENT: {
        OrderStatus.CONFIRMED,
        OrderStatus.PAYMENT_FAILED,
        OrderStatus.CANCELLED,
    },
    OrderStatus.PAYMENT_FAILED: {
        OrderStatus.PENDING_PAYMENT,
        OrderStatus.CANCELLED,
    },
    OrderStatus.CONFIRMED: {
        OrderStatus.FULFILLING,
        OrderStatus.CANCELLED,
    },
    OrderStatus.FULFILLING: {
        OrderStatus.OUT_FOR_DELIVERY,
        OrderStatus.CANCELLED,
    },
    OrderStatus.OUT_FOR_DELIVERY: {
        OrderStatus.DELIVERED,
        OrderStatus.CANCELLED,
    },
    OrderStatus.DELIVERED: {
        OrderStatus.REFUNDED,
    },
    OrderStatus.CANCELLED: set(),
    OrderStatus.REFUNDED: set(),
}


def can_transition(current: OrderStatus, target: OrderStatus) -> bool:
    """Check if transitioning from current to target OrderStatus is valid."""
    allowed = TRANSITIONS.get(current, set())
    return target in allowed
