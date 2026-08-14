"""Canonical RBAC permissions across platform domain services."""

from __future__ import annotations
from .authorization import require_permission


class Permission:
    """Standard permission string constants."""

    ORDER_READ = "order:read"
    ORDER_CREATE = "order:create"
    ORDER_CANCEL = "order:cancel"

    PAYMENT_READ = "payment:read"
    PAYMENT_AUTHORIZE = "payment:authorize"
    PAYMENT_REFUND = "payment:refund"

    INVENTORY_READ = "inventory:read"
    INVENTORY_RESERVE = "inventory:reserve"

    DELIVERY_READ = "delivery:read"
    DELIVERY_ASSIGN = "delivery:assign"

    VERIFICATION_READ = "verification:read"
    VERIFICATION_SUBMIT = "verification:submit"

    ADMIN_READ = "admin:read"
    ADMIN_WRITE = "admin:write"


__all__ = ["Permission", "require_permission"]
