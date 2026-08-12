"""Roles and permissions — RBAC."""

from __future__ import annotations

from enum import Enum


class Role(str, Enum):
    """All roles recognized by the platform."""

    # Platform / System
    PLATFORM_ROOT = "PLATFORM_ROOT"

    # Administrative
    SUPER_ADMIN = "SUPER_ADMIN"
    REGULATORY_ADMIN = "REGULATORY_ADMIN"
    STATE_ADMIN = "STATE_ADMIN"
    DISTRICT_ADMIN = "DISTRICT_ADMIN"
    CITY_ADMIN = "CITY_ADMIN"
    COMPLIANCE_OFFICER = "COMPLIANCE_OFFICER"
    SECURITY_ADMIN = "SECURITY_ADMIN"
    DATA_PROTECTION_OFFICER = "DATA_PROTECTION_OFFICER"
    FINANCE_ADMIN = "FINANCE_ADMIN"
    AUDITOR = "AUDITOR"

    # Retailer
    RETAILER_OWNER = "RETAILER_OWNER"
    ORG_ADMIN = "ORG_ADMIN"
    REGIONAL_MANAGER = "REGIONAL_MANAGER"
    STORE_MANAGER = "STORE_MANAGER"
    STORE_OPERATOR = "STORE_OPERATOR"
    INVENTORY_MANAGER = "INVENTORY_MANAGER"
    PRICING_MANAGER = "PRICING_MANAGER"
    ORDER_MANAGER = "ORDER_MANAGER"
    PACKER = "PACKER"

    # Fulfillment
    FLEET_OWNER = "FLEET_OWNER"
    FLEET_MANAGER = "FLEET_MANAGER"
    DISPATCHER = "DISPATCHER"
    DELIVERY_AGENT = "DELIVERY_AGENT"

    # Consumer
    CONSUMER = "CONSUMER"
    GUEST = "GUEST"
    BUSINESS_BUYER = "BUSINESS_BUYER"

    # Support
    SUPPORT_AGENT = "SUPPORT_AGENT"

    # Service / System
    SERVICE = "SERVICE"



class Permission(str, Enum):
    """Atomic permissions: RESOURCE.ACTION."""

    # Consumer
    CONSUMER_ORDER_CREATE = "consumer:order:create"
    CONSUMER_ORDER_READ_OWN = "consumer:order:read:own"
    CONSUMER_ORDER_CANCEL_OWN = "consumer:order:cancel:own"
    CONSUMER_PROFILE_READ_OWN = "consumer:profile:read:own"
    CONSUMER_PROFILE_UPDATE_OWN = "consumer:profile:update:own"
    CONSUMER_VERIFICATION_START = "consumer:verification:start"
    CONSUMER_DELIVERY_CONFIRM = "consumer:delivery:confirm"

    # Retailer
    RETAILER_ORG_READ_OWN = "retailer:org:read:own"
    RETAILER_STORE_READ_OWN = "retailer:store:read:own"
    RETAILER_STORE_UPDATE_OWN = "retailer:store:update:own"
    RETAILER_STAFF_MANAGE = "retailer:staff:manage"
    RETAILER_INVENTORY_READ_OWN = "retailer:inventory:read:own"
    RETAILER_INVENTORY_ADJUST = "retailer:inventory:adjust"
    RETAILER_ORDER_READ_OWN = "retailer:order:read:own"
    RETAILER_ORDER_ACCEPT = "retailer:order:accept"
    RETAILER_ORDER_PACK = "retailer:order:pack"
    RETAILER_PRICING_MANAGE = "retailer:pricing:manage"

    # Fulfillment
    DELIVERY_ORDER_READ_ASSIGNED = "delivery:order:read:assigned"
    DELIVERY_PICKUP_CONFIRM = "delivery:pickup:confirm"
    DELIVERY_HANDOVER_COMPLETE = "delivery:handover:complete"
    DELIVERY_PROOF_UPLOAD = "delivery:proof:upload"
    DELIVERY_LOCATION_UPDATE = "delivery:location:update"

    # Admin
    ADMIN_POLICY_CREATE = "admin:policy:create"
    ADMIN_POLICY_APPROVE = "admin:policy:approve"
    ADMIN_POLICY_ACTIVATE = "admin:policy:activate"
    ADMIN_RETAILER_APPROVE = "admin:retailer:approve"
    ADMIN_LICENSE_APPROVE = "admin:license:approve"
    ADMIN_LICENSE_REVOKE = "admin:license:revoke"
    ADMIN_AUDIT_READ = "admin:audit:read"
    ADMIN_AUDIT_EXPORT = "admin:audit:export"

    # System
    SYSTEM_INTERNAL = "system:internal"


# Role -> Permissions mapping
ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.CONSUMER: frozenset({
        Permission.CONSUMER_ORDER_CREATE,
        Permission.CONSUMER_ORDER_READ_OWN,
        Permission.CONSUMER_ORDER_CANCEL_OWN,
        Permission.CONSUMER_PROFILE_READ_OWN,
        Permission.CONSUMER_PROFILE_UPDATE_OWN,
        Permission.CONSUMER_VERIFICATION_START,
        Permission.CONSUMER_DELIVERY_CONFIRM,
    }),
    Role.STORE_MANAGER: frozenset({
        Permission.RETAILER_ORG_READ_OWN,
        Permission.RETAILER_STORE_READ_OWN,
        Permission.RETAILER_STORE_UPDATE_OWN,
        Permission.RETAILER_STAFF_MANAGE,
        Permission.RETAILER_INVENTORY_READ_OWN,
        Permission.RETAILER_INVENTORY_ADJUST,
        Permission.RETAILER_ORDER_READ_OWN,
        Permission.RETAILER_ORDER_ACCEPT,
        Permission.RETAILER_ORDER_PACK,
        Permission.RETAILER_PRICING_MANAGE,
    }),
    Role.DELIVERY_AGENT: frozenset({
        Permission.DELIVERY_ORDER_READ_ASSIGNED,
        Permission.DELIVERY_PICKUP_CONFIRM,
        Permission.DELIVERY_HANDOVER_COMPLETE,
        Permission.DELIVERY_PROOF_UPLOAD,
        Permission.DELIVERY_LOCATION_UPDATE,
    }),
    Role.SUPER_ADMIN: frozenset(p for p in Permission),
    Role.AUDITOR: frozenset({
        Permission.ADMIN_AUDIT_READ,
        Permission.ADMIN_AUDIT_EXPORT,
    }),
    Role.SERVICE: frozenset({Permission.SYSTEM_INTERNAL}),
}


def has_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, frozenset())


def get_permissions_for_role(role: Role) -> frozenset[Permission]:
    return ROLE_PERMISSIONS.get(role, frozenset())
