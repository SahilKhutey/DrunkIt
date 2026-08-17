"""Order domain package."""

from .enums import CartStatus, FulfillmentStatus, OrderStatus, PaymentStatus
from .events import OrderCreatedEvent
from .exceptions import (
    ComplianceCheckFailedError,
    DuplicateIdempotencyKeyError,
    InvalidStateTransitionError,
    OrderDomainError,
    OrderNotFoundError,
)
from .state_machine import TRANSITIONS, can_transition

__all__ = [
    "TRANSITIONS",
    "CartStatus",
    "ComplianceCheckFailedError",
    "DuplicateIdempotencyKeyError",
    "FulfillmentStatus",
    "InvalidStateTransitionError",
    "OrderCreatedEvent",
    "OrderDomainError",
    "OrderNotFoundError",
    "OrderStatus",
    "PaymentStatus",
    "can_transition",
]
