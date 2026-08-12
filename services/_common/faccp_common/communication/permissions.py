"""
Service Permission Matrix.
Defines explicit caller -> target service communication boundaries.
"""

from __future__ import annotations

from typing import ClassVar


class ServicePermissionMatrix:
    PERMISSIONS: ClassVar[dict[tuple[str, str], list[str]]] = {
        ("checkout-service", "inventory-service"): ["reserve", "release"],
        ("checkout-service", "compliance-service"): ["evaluate"],
        ("checkout-service", "payment-service"): ["create_intent"],
        ("order-service", "notification-service"): ["publish"],
        ("delivery-service", "verification-service"): ["validate"],
        ("analytics-service", "order-service"): ["read_events"],
        ("admin-service", "audit-service"): ["read"],
        ("compliance-service", "order-service"): ["read"],
        # Explicit denial example
        ("consumer-service", "payment-service"): [],
    }

    @classmethod
    def is_allowed(cls, caller: str, target: str, action: str) -> bool:
        allowed_actions = cls.PERMISSIONS.get((caller, target), [])
        return action in allowed_actions
