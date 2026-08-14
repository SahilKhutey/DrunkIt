"""Service identity models and Security Context definition."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ServiceIdentity:
    """Service Identity definition for service-to-service authorization."""

    service_name: str
    permissions: frozenset[str]


@dataclass
class SecurityContext:
    """Request Security Context attached to execution thread/context."""

    subject: str | None = None
    service: str | None = None
    roles: tuple[str, ...] = ()
    permissions: tuple[str, ...] = ()
    request_id: str | None = None
    correlation_id: str | None = None


ORDER_SERVICE = ServiceIdentity(
    service_name="order-service",
    permissions=frozenset({"order:read", "order:create", "order:cancel"}),
)

PAYMENT_SERVICE = ServiceIdentity(
    service_name="payment-service",
    permissions=frozenset({"payment:read", "payment:authorize", "payment:refund"}),
)

INVENTORY_SERVICE = ServiceIdentity(
    service_name="inventory-service",
    permissions=frozenset({"inventory:read", "inventory:reserve"}),
)

DELIVERY_SERVICE = ServiceIdentity(
    service_name="delivery-service",
    permissions=frozenset({"delivery:read", "delivery:assign"}),
)

TRUSTED_SERVICES = {
    "order-service": ORDER_SERVICE,
    "payment-service": PAYMENT_SERVICE,
    "inventory-service": INVENTORY_SERVICE,
    "delivery-service": DELIVERY_SERVICE,
}
