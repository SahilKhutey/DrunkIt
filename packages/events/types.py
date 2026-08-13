class EventType:

    ORDER_CREATED = "order.created"

    ORDER_CANCELLED = "order.cancelled"

    SERVICEABILITY_CHECKED = (
        "serviceability.checked"
    )

    STORE_SELECTED = (
        "fulfilment.store_selected"
    )

    INVENTORY_RESERVED = (
        "inventory.reserved"
    )

    INVENTORY_RELEASED = (
        "inventory.released"
    )

    FULFILMENT_READY = (
        "fulfilment.ready"
    )

    DELIVERY_CREATED = (
        "delivery.created"
    )

    DELIVERY_DISPATCHING = (
        "delivery.dispatching"
    )

    DRIVER_RESERVED = (
        "driver.reserved"
    )

    DRIVER_ASSIGNED = (
        "driver.assigned"
    )

    DELIVERY_PICKED_UP = (
        "delivery.picked_up"
    )

    DELIVERY_COMPLETED = (
        "delivery.completed"
    )
