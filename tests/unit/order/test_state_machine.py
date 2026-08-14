"""Unit tests for Order state machine rules."""

from services.order.app.domain.enums import OrderStatus
from services.order.app.domain.state_machine import can_transition


def test_draft_to_compliance():
    assert can_transition(OrderStatus.DRAFT, OrderStatus.PENDING_COMPLIANCE) is True


def test_draft_cannot_be_delivered():
    assert can_transition(OrderStatus.DRAFT, OrderStatus.DELIVERED) is False


def test_compliance_failed_cannot_confirm():
    assert can_transition(OrderStatus.COMPLIANCE_FAILED, OrderStatus.CONFIRMED) is False


def test_pending_payment_to_confirmed():
    assert can_transition(OrderStatus.PENDING_PAYMENT, OrderStatus.CONFIRMED) is True
