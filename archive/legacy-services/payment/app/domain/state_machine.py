"""Payment state machine transitions."""

from __future__ import annotations

from typing import Any
from .enums import PaymentStatus

TRANSITIONS: dict[PaymentStatus, set[PaymentStatus]] = {
    PaymentStatus.CREATED: {
        PaymentStatus.PROCESSING,
        PaymentStatus.REQUIRES_ACTION,
        PaymentStatus.CANCELLED,
        PaymentStatus.FAILED,
    },
    PaymentStatus.REQUIRES_ACTION: {
        PaymentStatus.PROCESSING,
        PaymentStatus.AUTHORIZED,
        PaymentStatus.CAPTURED,
        PaymentStatus.CANCELLED,
        PaymentStatus.FAILED,
    },
    PaymentStatus.PROCESSING: {
        PaymentStatus.AUTHORIZED,
        PaymentStatus.CAPTURED,
        PaymentStatus.FAILED,
    },
    PaymentStatus.AUTHORIZED: {
        PaymentStatus.CAPTURED,
        PaymentStatus.CANCELLED,
    },
    PaymentStatus.CAPTURED: {
        PaymentStatus.REFUND_PENDING,
    },
    PaymentStatus.REFUND_PENDING: {
        PaymentStatus.REFUNDED,
        PaymentStatus.PARTIALLY_REFUNDED,
    },
    PaymentStatus.PARTIALLY_REFUNDED: {
        PaymentStatus.REFUND_PENDING,
        PaymentStatus.REFUNDED,
    },
    PaymentStatus.FAILED: set(),
    PaymentStatus.CANCELLED: set(),
    PaymentStatus.REFUNDED: set(),
}


def can_transition(current: PaymentStatus, target: PaymentStatus) -> bool:
    """Check if transitioning from current to target PaymentStatus is valid."""
    allowed = TRANSITIONS.get(current, set())
    return target in allowed


def transition(payment: Any, target: PaymentStatus) -> Any:
    """Execute valid state transition on payment object or raise ValueError."""
    curr = getattr(payment, "status", None)
    if isinstance(curr, str):
        curr = PaymentStatus(curr)
    if not can_transition(curr, target):
        raise ValueError(f"Invalid payment transition: {curr} -> {target}")
    payment.status = target
    return payment
