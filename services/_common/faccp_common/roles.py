from __future__ import annotations

from enum import Enum


class Role(str, Enum):
    """All roles recognized by the platform."""

    # ---------- Platform / System ----------
    PLATFORM_ROOT = "PLATFORM_ROOT"

    # ---------- Administrative ----------
    SUPER_ADMIN = "SUPER_ADMIN"
    REGULATORY_ADMIN = "REGULATORY_ADMIN"
    STATE_ADMIN = "STATE_ADMIN"
    DISTRICT_ADMIN = "DISTRICT_ADMIN"
    CITY_ADMIN = "CITY_ADMIN"
    NATIONAL_LICENSING_AUTHORITY = "NATIONAL_LICENSING_AUTHORITY"
    EXCISE_INSPECTOR = "EXCISE_INSPECTOR"
    ZONAL_LICENSING_OFFICER = "ZONAL_LICENSING_OFFICER"
    COMPLIANCE_OFFICER = "COMPLIANCE_OFFICER"
    SECURITY_ADMIN = "SECURITY_ADMIN"
    FRAUD_INVESTIGATOR = "FRAUD_INVESTIGATOR"
    INCIDENT_RESPONDER = "INCIDENT_RESPONDER"
    SECURITY_ANALYST = "SECURITY_ANALYST"
    DATA_PROTECTION_OFFICER = "DATA_PROTECTION_OFFICER"
    FINANCE_ADMIN = "FINANCE_ADMIN"
    SETTLEMENT_OFFICER = "SETTLEMENT_OFFICER"
    RECONCILIATION_ANALYST = "RECONCILIATION_ANALYST"
    TAX_OFFICER = "TAX_OFFICER"
    SUPPORT_ADMIN = "SUPPORT_ADMIN"
    TIER_1_AGENT = "TIER_1_AGENT"
    TIER_2_AGENT = "TIER_2_AGENT"
    ESCALATION_MANAGER = "ESCALATION_MANAGER"
    AUDITOR = "AUDITOR"
    INTERNAL_AUDITOR = "INTERNAL_AUDITOR"
    EXTERNAL_AUDITOR = "EXTERNAL_AUDITOR"

    # ---------- Retailer ----------
    RETAILER_OWNER = "RETAILER_OWNER"
    ORG_ADMIN = "ORG_ADMIN"
    REGIONAL_MANAGER = "REGIONAL_MANAGER"
    STORE_MANAGER = "STORE_MANAGER"
    ASSISTANT_STORE_MANAGER = "ASSISTANT_STORE_MANAGER"
    INVENTORY_MANAGER = "INVENTORY_MANAGER"
    INVENTORY_STAFF = "INVENTORY_STAFF"
    STOCK_AUDITOR = "STOCK_AUDITOR"
    PRICING_MANAGER = "PRICING_MANAGER"
    ORDER_MANAGER = "ORDER_MANAGER"
    PACKER = "PACKER"
    DISPATCHER = "DISPATCHER"
    STORE_ACCOUNTANT = "STORE_ACCOUNTANT"
    FLEET_OWNER = "FLEET_OWNER"
    FLEET_MANAGER = "FLEET_MANAGER"
    DISPATCH_SUPERVISOR = "DISPATCH_SUPERVISOR"
    DELIVERY_AGENT = "DELIVERY_AGENT"
    SENIOR_AGENT = "SENIOR_AGENT"
    JUNIOR_AGENT = "JUNIOR_AGENT"
    FLEET_ACCOUNTANT = "FLEET_ACCOUNTANT"
    HR_ADMIN = "HR_ADMIN"
    FINANCE_MANAGER = "FINANCE_MANAGER"
    STORE_AUDITOR = "STORE_AUDITOR"

    # ---------- Consumer ----------
    CONSUMER = "CONSUMER"
    GUEST = "GUEST"
    BUSINESS_BUYER = "BUSINESS_BUYER"
    ORG_BUYER_REP = "ORG_BUYER_REP"
    ORG_BUYER_APPROVER = "ORG_BUYER_APPROVER"
    TRUSTED_BUYER = "TRUSTED_BUYER"


class ConsumerLevel(str, Enum):
    """Consumer trust progression (C0-C4)."""

    C0_GUEST = "C0_GUEST"
    C1_REGISTERED = "C1_REGISTERED"
    C2_IDENTITY_VERIFIED = "C2_IDENTITY_VERIFIED"
    C3_AGE_ELIGIBLE = "C3_AGE_ELIGIBLE"
    C4_TRANSACTION_VERIFIED = "C4_TRANSACTION_VERIFIED"


class SellerLevel(str, Enum):
    """Seller trust progression (S0-S5)."""

    S0_APPLICATION = "S0_APPLICATION"
    S1_BUSINESS_VERIFIED = "S1_BUSINESS_VERIFIED"
    S2_LICENSE_VERIFIED = "S2_LICENSE_VERIFIED"
    S3_STORE_VERIFIED = "S3_STORE_VERIFIED"
    S4_OPERATIONALLY_VERIFIED = "S4_OPERATIONALLY_VERIFIED"
    S5_FULLY_COMPLIANT = "S5_FULLY_COMPLIANT"


class Permission(str, Enum):
    """Atomic permission identifiers."""

    # Consumer
    CONSUMER_PROFILE_READ_SELF = "consumer:profile:read:self"
    CONSUMER_PROFILE_UPDATE_SELF = "consumer:profile:update:self"
    CONSUMER_IDENTITY_SUBMIT = "consumer:identity:submit"
    CONSUMER_AGE_VERIFY = "consumer:age:verify"
    CONSUMER_ORDER_CREATE = "consumer:order:create"
    CONSUMER_ORDER_READ_SELF = "consumer:order:read:self"
    CONSUMER_DELIVERY_CONFIRM = "consumer:delivery:confirm"

    # Retailer
    RETAILER_ORG_READ_OWN = "retailer:org:read:own"
    RETAILER_ORG_UPDATE_OWN = "retailer:org:update:own"
    RETAILER_STORE_READ_OWN = "retailer:store:read:own"
    RETAILER_STORE_CREATE = "retailer:store:create"
    RETAILER_STORE_UPDATE_OWN = "retailer:store:update:own"
    RETAILER_STAFF_CREATE = "retailer:staff:create"
    RETAILER_STAFF_READ_OWN = "retailer:staff:read:own"
    RETAILER_LICENSE_SUBMIT = "retailer:license:submit"
    RETAILER_LICENSE_READ_OWN = "retailer:license:read:own"
    RETAILER_INVENTORY_READ_OWN = "retailer:inventory:read:own"
    RETAILER_INVENTORY_ADJUST = "retailer:inventory:adjust"
    RETAILER_PRICING_MANAGE = "retailer:pricing:manage"
    RETAILER_ORDER_READ_OWN = "retailer:order:read:own"
    RETAILER_ORDER_ACCEPT = "retailer:order:accept"
    RETAILER_ORDER_PACK = "retailer:order:pack"
    RETAILER_ORDER_DISPATCH = "retailer:order:dispatch"

    # Admin
    ADMIN_JURISDICTION_MANAGE = "admin:jurisdiction:manage"
    ADMIN_POLICY_MANAGE = "admin:policy:manage"
    ADMIN_RETAILER_APPROVE = "admin:retailer:approve"
    ADMIN_RETAILER_SUSPEND = "admin:retailer:suspend"
    ADMIN_LICENSE_VERIFY = "admin:license:verify"
    ADMIN_LICENSE_REVOKE = "admin:license:revoke"
    ADMIN_CONSUMER_READ_AGGREGATED = "admin:consumer:read:aggregated"
    ADMIN_RISK_INVESTIGATE = "admin:risk:investigate"
    ADMIN_AUDIT_READ = "admin:audit:read"
    ADMIN_AUDIT_EXPORT = "admin:audit:export"
    ADMIN_DSAR_HANDLE = "admin:dsar:handle"
    ADMIN_REFUND_APPROVE = "admin:refund:approve"
    ADMIN_FRAUD_HANDLE = "admin:fraud:handle"

    # Delivery
    DELIVERY_ORDER_READ_ASSIGNED = "delivery:order:read:assigned"
    DELIVERY_VERIFICATION_PERFORM = "delivery:verification:perform"
    DELIVERY_PROOF_UPLOAD = "delivery:proof:upload"
    DELIVERY_INCIDENT_REPORT = "delivery:incident:report"


ROLE_PERMISSIONS: dict[Role, frozenset[Permission]] = {
    Role.CONSUMER: frozenset(
        {
            Permission.CONSUMER_PROFILE_READ_SELF,
            Permission.CONSUMER_PROFILE_UPDATE_SELF,
            Permission.CONSUMER_IDENTITY_SUBMIT,
            Permission.CONSUMER_AGE_VERIFY,
            Permission.CONSUMER_ORDER_CREATE,
            Permission.CONSUMER_ORDER_READ_SELF,
            Permission.CONSUMER_DELIVERY_CONFIRM,
        }
    ),
    Role.STORE_MANAGER: frozenset(
        {
            Permission.RETAILER_ORG_READ_OWN,
            Permission.RETAILER_STORE_READ_OWN,
            Permission.RETAILER_STORE_UPDATE_OWN,
            Permission.RETAILER_STAFF_READ_OWN,
            Permission.RETAILER_STAFF_CREATE,
            Permission.RETAILER_LICENSE_READ_OWN,
            Permission.RETAILER_INVENTORY_READ_OWN,
            Permission.RETAILER_INVENTORY_ADJUST,
            Permission.RETAILER_PRICING_MANAGE,
            Permission.RETAILER_ORDER_READ_OWN,
            Permission.RETAILER_ORDER_ACCEPT,
            Permission.RETAILER_ORDER_PACK,
            Permission.RETAILER_ORDER_DISPATCH,
        }
    ),
    Role.DELIVERY_AGENT: frozenset(
        {
            Permission.DELIVERY_ORDER_READ_ASSIGNED,
            Permission.DELIVERY_VERIFICATION_PERFORM,
            Permission.DELIVERY_PROOF_UPLOAD,
            Permission.DELIVERY_INCIDENT_REPORT,
        }
    ),
    Role.REGULATORY_ADMIN: frozenset(
        {
            Permission.ADMIN_JURISDICTION_MANAGE,
            Permission.ADMIN_POLICY_MANAGE,
            Permission.ADMIN_RETAILER_APPROVE,
            Permission.ADMIN_RETAILER_SUSPEND,
            Permission.ADMIN_LICENSE_VERIFY,
            Permission.ADMIN_LICENSE_REVOKE,
            Permission.ADMIN_RISK_INVESTIGATE,
            Permission.ADMIN_AUDIT_READ,
        }
    ),
    Role.SUPER_ADMIN: frozenset(Permission),
    Role.AUDITOR: frozenset(
        {
            Permission.ADMIN_AUDIT_READ,
            Permission.ADMIN_AUDIT_EXPORT,
            Permission.RETAILER_ORG_READ_OWN,
            Permission.RETAILER_STORE_READ_OWN,
            Permission.ADMIN_CONSUMER_READ_AGGREGATED,
        }
    ),
}


def has_permission(role: Role, permission: Permission) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, frozenset())


def get_permissions(role: Role) -> frozenset[Permission]:
    return ROLE_PERMISSIONS.get(role, frozenset())
