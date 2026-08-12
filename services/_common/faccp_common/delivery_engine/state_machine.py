"""
Delivery Lifecycle State Machine & Driver States.
"""

from __future__ import annotations

from enum import Enum
from typing import ClassVar


class DeliveryStatus(str, Enum):
    REQUESTED = "REQUESTED"
    PLANNING = "PLANNING"
    DISPATCHING = "DISPATCHING"
    ASSIGNED = "ASSIGNED"
    PICKUP_READY = "PICKUP_READY"
    PICKED_UP = "PICKED_UP"
    IN_TRANSIT = "IN_TRANSIT"
    ARRIVING = "ARRIVING"
    HANDOFF_CHECK = "HANDOFF_CHECK"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"
    RETURN_REQUIRED = "RETURN_REQUIRED"
    RETURNED = "RETURNED"


class DriverState(str, Enum):
    OFFLINE = "OFFLINE"
    AVAILABLE = "AVAILABLE"
    RESERVED = "RESERVED"
    ASSIGNED = "ASSIGNED"
    PICKING_UP = "PICKING_UP"
    DELIVERING = "DELIVERING"
    PAUSED = "PAUSED"
    OFFLINE_PENDING = "OFFLINE_PENDING"
    SUSPENDED = "SUSPENDED"


class VerificationState(str, Enum):
    NOT_REQUIRED = "NOT_REQUIRED"
    REQUIRED = "REQUIRED"
    IN_PROGRESS = "IN_PROGRESS"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
    BLOCKED = "BLOCKED"


class DeliveryStateMachine:
    """Manages valid delivery status transitions."""

    ALLOWED_TRANSITIONS: ClassVar[dict[DeliveryStatus, set[DeliveryStatus]]] = {
        DeliveryStatus.REQUESTED: {DeliveryStatus.PLANNING, DeliveryStatus.CANCELLED, DeliveryStatus.FAILED},
        DeliveryStatus.PLANNING: {DeliveryStatus.DISPATCHING, DeliveryStatus.CANCELLED, DeliveryStatus.FAILED},
        DeliveryStatus.DISPATCHING: {DeliveryStatus.ASSIGNED, DeliveryStatus.CANCELLED, DeliveryStatus.FAILED},
        DeliveryStatus.ASSIGNED: {DeliveryStatus.PICKUP_READY, DeliveryStatus.CANCELLED, DeliveryStatus.FAILED},
        DeliveryStatus.PICKUP_READY: {DeliveryStatus.PICKED_UP, DeliveryStatus.CANCELLED, DeliveryStatus.FAILED},
        DeliveryStatus.PICKED_UP: {DeliveryStatus.IN_TRANSIT, DeliveryStatus.FAILED, DeliveryStatus.RETURN_REQUIRED},
        DeliveryStatus.IN_TRANSIT: {DeliveryStatus.ARRIVING, DeliveryStatus.FAILED, DeliveryStatus.RETURN_REQUIRED},
        DeliveryStatus.ARRIVING: {DeliveryStatus.HANDOFF_CHECK, DeliveryStatus.FAILED, DeliveryStatus.RETURN_REQUIRED},
        DeliveryStatus.HANDOFF_CHECK: {DeliveryStatus.DELIVERED, DeliveryStatus.FAILED, DeliveryStatus.RETURN_REQUIRED},
        DeliveryStatus.DELIVERED: set(),
        DeliveryStatus.RETURN_REQUIRED: {DeliveryStatus.RETURNED},
        DeliveryStatus.RETURNED: set(),
        DeliveryStatus.CANCELLED: set(),
        DeliveryStatus.FAILED: set(),
    }

    @classmethod
    def can_transition(cls, current: DeliveryStatus, target: DeliveryStatus) -> bool:
        return target in cls.ALLOWED_TRANSITIONS.get(current, set())
