"""
Order state machine.

Defines valid state transitions for the order lifecycle.
Anything not in TRANSITIONS is rejected.
"""

from __future__ import annotations

from enum import Enum
from typing import Any


class OrderState(str, Enum):
    CREATED = "CREATED"
    VALIDATING = "VALIDATING"
    COMPLIANCE_CHECK = "COMPLIANCE_CHECK"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    CONFIRMED = "CONFIRMED"
    RETAILER_ACCEPTED = "RETAILER_ACCEPTED"
    PICKING = "PICKING"
    PACKED = "PACKED"
    READY_FOR_PICKUP = "READY_FOR_PICKUP"
    DRIVER_ASSIGNED = "DRIVER_ASSIGNED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERY_VERIFICATION = "DELIVERY_VERIFICATION"
    DELIVERED = "DELIVERED"

    # Failure / terminal states
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    PAYMENT_FAILED = "PAYMENT_FAILED"
    VERIFICATION_FAILED = "VERIFICATION_FAILED"
    COMPLIANCE_BLOCKED = "COMPLIANCE_BLOCKED"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    DELIVERY_FAILED = "DELIVERY_FAILED"
    REFUND_PENDING = "REFUND_PENDING"
    REFUNDED = "REFUNDED"


TRANSITIONS: dict[OrderState, set[OrderState]] = {
    OrderState.CREATED: {OrderState.VALIDATING, OrderState.CANCELLED},
    OrderState.VALIDATING: {OrderState.COMPLIANCE_CHECK, OrderState.REJECTED, OrderState.CANCELLED},
    OrderState.COMPLIANCE_CHECK: {
        OrderState.PAYMENT_PENDING, OrderState.COMPLIANCE_BLOCKED, OrderState.CANCELLED
    },
    OrderState.PAYMENT_PENDING: {OrderState.CONFIRMED, OrderState.PAYMENT_FAILED, OrderState.CANCELLED},
    OrderState.CONFIRMED: {
        OrderState.RETAILER_ACCEPTED, OrderState.OUT_OF_STOCK, OrderState.CANCELLED
    },
    OrderState.RETAILER_ACCEPTED: {OrderState.PICKING, OrderState.CANCELLED},
    OrderState.PICKING: {OrderState.PACKED, OrderState.OUT_OF_STOCK},
    OrderState.PACKED: {OrderState.READY_FOR_PICKUP},
    OrderState.READY_FOR_PICKUP: {OrderState.DRIVER_ASSIGNED},
    OrderState.DRIVER_ASSIGNED: {OrderState.IN_TRANSIT, OrderState.DELIVERY_FAILED},
    OrderState.IN_TRANSIT: {OrderState.DELIVERY_VERIFICATION, OrderState.DELIVERY_FAILED},
    OrderState.DELIVERY_VERIFICATION: {OrderState.DELIVERED, OrderState.VERIFICATION_FAILED},
    OrderState.DELIVERED: {OrderState.REFUND_PENDING},
    OrderState.PAYMENT_FAILED: {OrderState.CANCELLED, OrderState.REFUND_PENDING},
    OrderState.VERIFICATION_FAILED: {OrderState.REFUND_PENDING, OrderState.DELIVERY_FAILED},
    OrderState.DELIVERY_FAILED: {OrderState.READY_FOR_PICKUP, OrderState.REFUND_PENDING},
    OrderState.REFUND_PENDING: {OrderState.REFUNDED},
    OrderState.CANCELLED: set(),
    OrderState.REJECTED: set(),
    OrderState.COMPLIANCE_BLOCKED: set(),
    OrderState.OUT_OF_STOCK: set(),
    OrderState.REFUNDED: set(),
}


def can_transition(current: OrderState, target: OrderState) -> bool:
    return target in TRANSITIONS.get(current, set())


def assert_transition(current: OrderState, target: OrderState) -> None:
    if not can_transition(current, target):
        from faccp_common.exceptions import StateTransitionError
        raise StateTransitionError(
            f"Invalid state transition: {current.value} → {target.value}",
            details={"current_state": current.value, "target_state": target.value},
        )


def is_terminal(state: OrderState) -> bool:
    return len(TRANSITIONS.get(state, set())) == 0
