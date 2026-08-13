"""Whitelabel service: Multi-Tenant Branding & Domain Routing Engine."""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.exceptions import NotFoundError
from faccp_common.logging import get_logger

from app.db.models import CustomDomainBinding, TenantBrandingConfig
from app.schemas.whitelabel import DomainBindingCreate, TenantBrandingCreate

logger = get_logger(__name__)


class WhitelabelService:
    """Whitelabel multi-tenant branding & custom CNAME domain manager."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def update_branding(self, payload: TenantBrandingCreate) -> TenantBrandingConfig:
        result = await self.db.execute(
            select(TenantBrandingConfig).where(TenantBrandingConfig.tenant_id == payload.tenant_id)
        )
        branding = result.scalar_one_or_none()
        if not branding:
            branding = TenantBrandingConfig(
                tenant_id=payload.tenant_id,
                brand_name=payload.brand_name,
                logo_url=payload.logo_url,
                primary_color_hex=payload.primary_color_hex,
                secondary_color_hex=payload.secondary_color_hex,
            )
            self.db.add(branding)
        else:
            branding.brand_name = payload.brand_name
            branding.logo_url = payload.logo_url
            branding.primary_color_hex = payload.primary_color_hex
            branding.secondary_color_hex = payload.secondary_color_hex

        await self.db.commit()
        await self.db.refresh(branding)
        return branding

    async def get_branding(self, tenant_id: str) -> TenantBrandingConfig:
        result = await self.db.execute(
            select(TenantBrandingConfig).where(TenantBrandingConfig.tenant_id == tenant_id)
        )
        branding = result.scalar_one_or_none()
        if not branding:
            raise NotFoundError(f"Branding config for tenant {tenant_id} not found")
        return branding

    async def bind_domain(self, payload: DomainBindingCreate) -> CustomDomainBinding:
        binding = CustomDomainBinding(
            tenant_id=payload.tenant_id,
            domain_name=payload.domain_name,
            ssl_certified=True,
            status="ACTIVE",
        )
        self.db.add(binding)
        await self.db.commit()
        await self.db.refresh(binding)
        return binding
