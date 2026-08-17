from app.domain.delivery.enums import DeliveryStatus


TRANSITIONS: dict[DeliveryStatus, set[DeliveryStatus]] = {
    DeliveryStatus.REQUESTED: {
        DeliveryStatus.PLANNING,
        DeliveryStatus.CANCELLED,
    },

    DeliveryStatus.PLANNING: {
        DeliveryStatus.DISPATCHING,
        DeliveryStatus.FAILED,
        DeliveryStatus.CANCELLED,
    },

    DeliveryStatus.DISPATCHING: {
        DeliveryStatus.ASSIGNED,
        DeliveryStatus.FAILED,
        DeliveryStatus.CANCELLED,
    },

    DeliveryStatus.ASSIGNED: {
        DeliveryStatus.PICKUP_READY,
        DeliveryStatus.CANCELLED,
        DeliveryStatus.FAILED,
    },

    DeliveryStatus.PICKUP_READY: {
        DeliveryStatus.PICKED_UP,
        DeliveryStatus.FAILED,
        DeliveryStatus.CANCELLED,
    },

    DeliveryStatus.PICKED_UP: {
        DeliveryStatus.IN_TRANSIT,
        DeliveryStatus.FAILED,
    },

    DeliveryStatus.IN_TRANSIT: {
        DeliveryStatus.ARRIVING,
        DeliveryStatus.FAILED,
    },

    DeliveryStatus.ARRIVING: {
        DeliveryStatus.HANDOFF_PENDING,
        DeliveryStatus.FAILED,
    },

    DeliveryStatus.HANDOFF_PENDING: {
        DeliveryStatus.DELIVERED,
        DeliveryStatus.FAILED,
        DeliveryStatus.RETURN_REQUIRED,
    },

    DeliveryStatus.RETURN_REQUIRED: {
        DeliveryStatus.RETURNED,
        DeliveryStatus.FAILED,
    },

    DeliveryStatus.RETURNED: set(),
    DeliveryStatus.DELIVERED: set(),
    DeliveryStatus.FAILED: set(),
    DeliveryStatus.CANCELLED: set(),
}


def can_transition(
    current: DeliveryStatus,
    target: DeliveryStatus,
) -> bool:
    return target in TRANSITIONS.get(current, set())


def validate_transition(
    current: DeliveryStatus,
    target: DeliveryStatus,
) -> None:
    if not can_transition(current, target):
        raise ValueError(
            f"Invalid delivery transition: "
            f"{current.value} -> {target.value}"
        )
