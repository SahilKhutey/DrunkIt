DELIVERY_TRANSITIONS = {
    "CREATED": {
        "READY_FOR_DISPATCH",
        "CANCELLED",
    },
    "READY_FOR_DISPATCH": {
        "DISPATCH_QUEUED",
        "CANCELLED",
    },
    "DISPATCH_QUEUED": {
        "ASSIGNMENT_PENDING",
        "CANCELLED",
    },
    "ASSIGNMENT_PENDING": {
        "ASSIGNED",
        "CANCELLED",
    },
    "ASSIGNED": {
        "PICKUP_PENDING",
        "CANCELLED",
    },
    "PICKUP_PENDING": {
        "PICKED_UP",
        "CANCELLED",
    },
    "PICKED_UP": {
        "IN_TRANSIT",
        "RETURN_REQUIRED",
    },
    "IN_TRANSIT": {
        "ARRIVING",
        "DELIVERY_FAILED",
        "RETURN_REQUIRED",
    },
    "ARRIVING": {
        "VERIFICATION_PENDING",
        "DELIVERY_FAILED",
    },
    "VERIFICATION_PENDING": {
        "VERIFIED",
        "DELIVERY_FAILED",
        "RETURN_REQUIRED",
    },
    "VERIFIED": {
        "HANDED_OVER",
        "DELIVERY_FAILED",
    },
    "HANDED_OVER": {
        "COMPLETED",
    },
    "DELIVERY_FAILED": {
        "RETURN_REQUIRED",
    },
    "RETURN_REQUIRED": {
        "RETURNED",
    },
    "RETURNED": set(),
    "COMPLETED": set(),
    "CANCELLED": set(),
}


def can_handover(delivery: dict) -> bool:
    if delivery.get("verification_required"):
        return delivery.get("status") == "VERIFIED"
    return delivery.get("status") in ("ARRIVING", "VERIFIED")
