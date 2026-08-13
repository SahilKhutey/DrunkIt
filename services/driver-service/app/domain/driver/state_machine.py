from app.domain.driver.enums import DriverOperationalStatus


TRANSITIONS = {
    DriverOperationalStatus.OFFLINE: {
        DriverOperationalStatus.AVAILABLE,
    },

    DriverOperationalStatus.AVAILABLE: {
        DriverOperationalStatus.OFFLINE,
        DriverOperationalStatus.RESERVED,
        DriverOperationalStatus.PAUSED,
    },

    DriverOperationalStatus.RESERVED: {
        DriverOperationalStatus.AVAILABLE,
        DriverOperationalStatus.ASSIGNED,
        DriverOperationalStatus.OFFLINE,
    },

    DriverOperationalStatus.ASSIGNED: {
        DriverOperationalStatus.PICKING_UP,
        DriverOperationalStatus.AVAILABLE,
    },

    DriverOperationalStatus.PICKING_UP: {
        DriverOperationalStatus.DELIVERING,
    },

    DriverOperationalStatus.DELIVERING: {
        DriverOperationalStatus.AVAILABLE,
        DriverOperationalStatus.OFFLINE,
    },

    DriverOperationalStatus.PAUSED: {
        DriverOperationalStatus.AVAILABLE,
        DriverOperationalStatus.OFFLINE,
    },
}


def can_transition(
    current: DriverOperationalStatus,
    target: DriverOperationalStatus,
) -> bool:
    return target in TRANSITIONS.get(current, set())


def validate_transition(
    current: DriverOperationalStatus,
    target: DriverOperationalStatus,
) -> None:

    if not can_transition(current, target):
        raise ValueError(
            f"Invalid driver transition: "
            f"{current.value} -> {target.value}"
        )
