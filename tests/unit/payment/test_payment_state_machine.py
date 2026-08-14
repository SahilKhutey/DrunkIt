"""Unit tests for Payment state machine transitions."""

import pytest
from services.payment.app.domain.enums import PaymentStatus
from services.payment.app.domain.state_machine import can_transition, transition


class DummyPayment:
    def __init__(self, status: PaymentStatus):
        self.status = status


def test_payment_capture_valid():
    payment = DummyPayment(PaymentStatus.AUTHORIZED)
    transition(payment, PaymentStatus.CAPTURED)
    assert payment.status == PaymentStatus.CAPTURED


def test_failed_payment_cannot_capture():
    payment = DummyPayment(PaymentStatus.FAILED)
    with pytest.raises(ValueError):
        transition(payment, PaymentStatus.CAPTURED)


def test_can_transition():
    assert can_transition(PaymentStatus.CREATED, PaymentStatus.PROCESSING) is True
    assert can_transition(PaymentStatus.FAILED, PaymentStatus.CAPTURED) is False
