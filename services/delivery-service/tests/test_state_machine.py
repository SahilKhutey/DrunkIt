import os
import sys
import pytest

delivery_service_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
if delivery_service_path not in sys.path:
    sys.path.insert(0, delivery_service_path)

from app.domain.delivery.enums import DeliveryStatus


from app.domain.delivery.state_machine import (
    can_transition,
    validate_transition,
)


def test_requested_to_planning():

    assert can_transition(
        DeliveryStatus.REQUESTED,
        DeliveryStatus.PLANNING,
    )


def test_invalid_requested_to_delivered():

    assert not can_transition(
        DeliveryStatus.REQUESTED,
        DeliveryStatus.DELIVERED,
    )


def test_invalid_transition_raises():

    with pytest.raises(ValueError):

        validate_transition(
            DeliveryStatus.REQUESTED,
            DeliveryStatus.DELIVERED,
        )


def test_full_successful_transition_path():
    path = [
        DeliveryStatus.REQUESTED,
        DeliveryStatus.PLANNING,
        DeliveryStatus.DISPATCHING,
        DeliveryStatus.ASSIGNED,
        DeliveryStatus.PICKUP_READY,
        DeliveryStatus.PICKED_UP,
        DeliveryStatus.IN_TRANSIT,
        DeliveryStatus.ARRIVING,
        DeliveryStatus.HANDOFF_PENDING,
        DeliveryStatus.DELIVERED,
    ]

    for current, target in zip(path[:-1], path[1:]):
        assert can_transition(current, target)
        validate_transition(current, target)
