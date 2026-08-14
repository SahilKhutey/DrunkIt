"""Integration test for event contracts and registry lookup."""

from faccp_platform.events.contracts import (
    InventoryReservedEvent,
    OrderCreatedEvent,
    PaymentAuthorizedEvent,
)
from faccp_platform.events.registry import get_event_contract


def test_order_created_contract():
    event = OrderCreatedEvent(
        order_id="order-001",
        consumer_id="consumer-001",
        total_amount=2500,
        currency="INR",
    )
    contract = get_event_contract("order.created")
    assert contract is OrderCreatedEvent
    payload = event.payload()
    assert payload["order_id"] == "order-001"
    assert payload["consumer_id"] == "consumer-001"
    assert payload["total_amount"] == 2500
    assert payload["currency"] == "INR"


def test_all_registered_contracts():
    assert get_event_contract("payment.authorized") is PaymentAuthorizedEvent
    assert get_event_contract("inventory.reserved") is InventoryReservedEvent
