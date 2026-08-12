"""Seed roles and permissions from Role/Permission enums."""

from __future__ import annotations

import asyncio
from sqlalchemy import select

from faccp_common.trust.roles import Permission, Role

from app.config import get_settings
from app.db.base import Base
from app.db.models import RoleDefinition
from faccp_common.database import init_engine, session_scope


ROLE_METADATA = {
    Role.PLATFORM_ROOT: {"domain": "system", "level": 100},
    Role.SUPER_ADMIN: {"domain": "admin", "level": 90},
    Role.REGULATORY_ADMIN: {"domain": "admin", "level": 80},
    Role.STATE_ADMIN: {"domain": "admin", "level": 70},
    Role.DISTRICT_ADMIN: {"domain": "admin", "level": 60},
    Role.CITY_ADMIN: {"domain": "admin", "level": 50},
    Role.COMPLIANCE_OFFICER: {"domain": "admin", "level": 50},
    Role.SECURITY_ADMIN: {"domain": "admin", "level": 80},
    Role.DATA_PROTECTION_OFFICER: {"domain": "admin", "level": 85},
    Role.FINANCE_ADMIN: {"domain": "admin", "level": 80},
    Role.AUDITOR: {"domain": "audit", "level": 75},
    Role.RETAILER_OWNER: {"domain": "retailer", "level": 90},
    Role.ORG_ADMIN: {"domain": "retailer", "level": 80},
    Role.REGIONAL_MANAGER: {"domain": "retailer", "level": 70},
    Role.STORE_MANAGER: {"domain": "retailer", "level": 60},
    Role.STORE_OPERATOR: {"domain": "retailer", "level": 50},
    Role.INVENTORY_MANAGER: {"domain": "retailer", "level": 55},
    Role.PRICING_MANAGER: {"domain": "retailer", "level": 55},
    Role.ORDER_MANAGER: {"domain": "retailer", "level": 55},
    Role.PACKER: {"domain": "retailer", "level": 35},
    Role.FLEET_OWNER: {"domain": "retailer", "level": 75},
    Role.FLEET_MANAGER: {"domain": "retailer", "level": 65},
    Role.DISPATCHER: {"domain": "retailer", "level": 55},
    Role.DELIVERY_AGENT: {"domain": "retailer", "level": 40},
    Role.CONSUMER: {"domain": "consumer", "level": 30},
    Role.GUEST: {"domain": "consumer", "level": 10},
    Role.BUSINESS_BUYER: {"domain": "consumer", "level": 40},
    Role.SUPPORT_AGENT: {"domain": "support", "level": 50},
}

ROLE_PERMISSIONS = {
    Role.CONSUMER: {Permission.CONSUMER_ORDER_CREATE, Permission.CONSUMER_ORDER_READ_OWN,
                    Permission.CONSUMER_ORDER_CANCEL_OWN, Permission.CONSUMER_PROFILE_READ_OWN,
                    Permission.CONSUMER_PROFILE_UPDATE_OWN, Permission.CONSUMER_VERIFICATION_START,
                    Permission.CONSUMER_DELIVERY_CONFIRM},
    Role.STORE_MANAGER: {Permission.RETAILER_ORG_READ_OWN, Permission.RETAILER_STORE_READ_OWN,
                          Permission.RETAILER_STORE_UPDATE_OWN, Permission.RETAILER_STAFF_MANAGE,
                          Permission.RETAILER_INVENTORY_READ_OWN, Permission.RETAILER_INVENTORY_ADJUST,
                          Permission.RETAILER_ORDER_READ_OWN, Permission.RETAILER_ORDER_ACCEPT,
                          Permission.RETAILER_ORDER_PACK, Permission.RETAILER_PRICING_MANAGE},
    Role.DELIVERY_AGENT: {Permission.DELIVERY_ORDER_READ_ASSIGNED, Permission.DELIVERY_PICKUP_CONFIRM,
                           Permission.DELIVERY_HANDOVER_COMPLETE, Permission.DELIVERY_PROOF_UPLOAD,
                           Permission.DELIVERY_LOCATION_UPDATE},
    Role.SUPER_ADMIN: set(Permission),
    Role.AUDITOR: {Permission.ADMIN_AUDIT_READ, Permission.ADMIN_AUDIT_EXPORT},
    Role.STATE_ADMIN: {Permission.ADMIN_RETAILER_APPROVE, Permission.ADMIN_LICENSE_APPROVE,
                       Permission.ADMIN_POLICY_APPROVE, Permission.ADMIN_AUDIT_READ},
    Role.REGULATORY_ADMIN: {Permission.ADMIN_POLICY_CREATE, Permission.ADMIN_POLICY_APPROVE,
                            Permission.ADMIN_POLICY_ACTIVATE, Permission.ADMIN_RETAILER_APPROVE,
                            Permission.ADMIN_LICENSE_APPROVE, Permission.ADMIN_LICENSE_REVOKE,
                            Permission.ADMIN_AUDIT_READ, Permission.ADMIN_AUDIT_EXPORT},
    Role.FINANCE_ADMIN: {Permission.ADMIN_AUDIT_READ, Permission.ADMIN_AUDIT_EXPORT},
    Role.DATA_PROTECTION_OFFICER: {Permission.ADMIN_AUDIT_READ, Permission.ADMIN_AUDIT_EXPORT},
    Role.SUPPORT_AGENT: {Permission.CONSUMER_ORDER_READ_OWN},
}


async def seed() -> None:
    settings = get_settings()
    init_engine(settings.database_url)
    async with session_scope() as session:
        for role, meta in ROLE_METADATA.items():
            existing = await session.execute(
                select(RoleDefinition).where(RoleDefinition.name == role.value)
            )
            role_def = existing.scalar_one_or_none()
            permissions = [p.value for p in ROLE_PERMISSIONS.get(role, set())]
            if role_def is None:
                role_def = RoleDefinition(
                    name=role.value, display_name=role.value.replace("_", " ").title(),
                    description=f"System role: {role.value}",
                    domain=meta["domain"], level=meta["level"],
                    parent_roles=[], permissions=permissions, is_system=True,
                )
                session.add(role_def)
            else:
                role_def.domain = meta["domain"]
                role_def.level = meta["level"]
                role_def.permissions = permissions
            print(f"  {role.value}: {len(permissions)} permissions")
    print(f"\n[OK] Seeded {len(ROLE_METADATA)} role definitions.")


if __name__ == "__main__":
    asyncio.run(seed())
