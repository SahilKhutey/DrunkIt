"""Event schema versioning validation and consumer contract protection."""

from __future__ import annotations


class UnsupportedEventVersion(Exception):
    """Raised when an event schema version is not supported by consumer."""

    def __init__(self, event_type: str, version: int) -> None:
        self.event_type = event_type
        self.version = version
        super().__init__(f"Unsupported schema version {version} for event type '{event_type}'")


SUPPORTED_VERSIONS: dict[str, set[int]] = {
    "order.created": {1},
    "order.cancelled": {1},
    "order.completed": {1},
    "payment.authorized": {1},
    "payment.failed": {1},
    "payment.refunded": {1},
    "inventory.reserved": {1},
    "inventory.released": {1},
    "compliance.approved": {1},
    "compliance.rejected": {1},
}


def validate_version(event_type: str, schema_version: int) -> bool:
    """Validate that schema_version is supported for event_type."""
    supported = SUPPORTED_VERSIONS.get(event_type, {1})
    if schema_version not in supported:
        raise UnsupportedEventVersion(event_type, schema_version)
    return True
