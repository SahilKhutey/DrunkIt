"""Unit tests for fulfillment and delivery state machines."""

import pytest
from services.fulfillment.app.domain.enums import DeliveryStatus, FulfillmentStatus
from services.fulfillment.app.domain.state_machine import (
    transition_delivery,
    transition_fulfillment,
)


def test_fulfillment_lifecycle():
    """Verify valid sequential transitions for fulfillment."""
    status = FulfillmentStatus.CREATED
    status = transition_fulfillment(status, FulfillmentStatus.RESERVING)
    status = transition_fulfillment(status, FulfillmentStatus.RESERVED)
    status = transition_fulfillment(status, FulfillmentStatus.PICKING)
    status = transition_fulfillment(status, FulfillmentStatus.PACKING)
    status = transition_fulfillment(status, FulfillmentStatus.READY_FOR_PICKUP)
    assert status == FulfillmentStatus.READY_FOR_PICKUP


def test_invalid_fulfillment_transition():
    """Verify invalid fulfillment transitions raise ValueError."""
    with pytest.raises(ValueError, match="Invalid fulfillment transition"):
        transition_fulfillment(FulfillmentStatus.CREATED, FulfillmentStatus.PACKING)


def test_delivery_lifecycle():
    """Verify valid sequential transitions for delivery."""
    status = DeliveryStatus.CREATED
    status = transition_delivery(status, DeliveryStatus.ASSIGNING)
    status = transition_delivery(status, DeliveryStatus.ASSIGNED)
    status = transition_delivery(status, DeliveryStatus.PICKED_UP)
    status = transition_delivery(status, DeliveryStatus.IN_TRANSIT)
    status = transition_delivery(status, DeliveryStatus.ARRIVED)
    status = transition_delivery(status, DeliveryStatus.VERIFICATION_PENDING)
    status = transition_delivery(status, DeliveryStatus.DELIVERED)
    assert status == DeliveryStatus.DELIVERED


def test_invalid_delivery_transition():
    """Verify skipping mandatory intermediate states raises ValueError."""
    with pytest.raises(ValueError, match="Invalid delivery transition"):
        transition_delivery(DeliveryStatus.CREATED, DeliveryStatus.DELIVERED)
