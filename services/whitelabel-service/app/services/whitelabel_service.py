"""White-label service — manages tenants, themes, domains, configs."""

import re
import secrets
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.events import make_event
from faccp_common.exceptions import ConflictError, NotFoundError, ValidationError
from faccp_common.kafka_client import EventProducer
from faccp_common.logging import get_logger
from app.config import get_settings
from app.db.models import CustomDomain, Tenant, TenantConfig, TenantTheme
from app.schemas.whitelabel import (
    CreateTenantRequest, CreateThemeRequest, TenantConfigRequest,
)

logger = get_logger(__name__)
settings = get_settings()


class WhiteLabelService:
    def __init__(self, db: AsyncSession, producer: EventProducer | None = None) -> None:
        self.db = db
        self.producer = producer

    async def create_tenant(self, payload: CreateTenantRequest) -> Tenant:
        if not re.match(r"^[a-z][a-z0-9-]{2,30}$", payload.code):
            raise ValidationError("Code must be lowercase letters, digits, hyphens, 3-31 chars, starting with letter")
        existing = await self._get_tenant_by_code(payload.code)
        if existing:
            raise ConflictError(f"Tenant with code '{payload.code}' already exists")
        tenant = Tenant(
            id=str(uuid.uuid4()), code=payload.code, name=payload.name,
            legal_name=payload.legal_name, primary_region=payload.primary_region,
            allowed_regions=payload.allowed_regions or [payload.primary_region],
            data_residency=payload.data_residency, subscription_tier=payload.subscription_tier,
            feature_flags=payload.feature_flags or {}, rate_limits=payload.rate_limits or {},
            contact_email=str(payload.contact_email), contact_phone=payload.contact_phone,
        )
        self.db.add(tenant)
        default_theme = TenantTheme(
            id=str(uuid.uuid4()), tenant_id=tenant.id, name="default",
            is_default=True, brand_name=payload.name, tagline="",
        )
        self.db.add(default_theme)
        await self.db.commit()
        await self.db.refresh(tenant)
        if self.producer:
            try:
                await self.producer.publish("tenant.events", make_event(
                    "tenant.created", {"tenant_id": tenant.id, "code": tenant.code,
                                       "name": tenant.name, "primary_region": tenant.primary_region},
                    producer=settings.service_name))
            except Exception:
                pass
        return tenant

    async def get_tenant(self, tenant_id: str) -> Tenant:
        result = await self.db.execute(select(Tenant).where(Tenant.id == tenant_id))
        t = result.scalar_one_or_none()
        if not t:
            raise NotFoundError("Tenant not found")
        return t

    async def get_tenant_by_code(self, code: str) -> Tenant:
        result = await self.db.execute(select(Tenant).where(Tenant.code == code))
        t = result.scalar_one_or_none()
        if not t:
            raise NotFoundError(f"Tenant '{code}' not found")
        return t

    async def create_theme(self, tenant_id: str, payload: CreateThemeRequest) -> TenantTheme:
        await self.get_tenant(tenant_id)
        if payload.is_default:
            await self.db.execute(
                update(TenantTheme).where(
                    TenantTheme.tenant_id == tenant_id,
                    TenantTheme.is_default.is_(True),
                ).values(is_default=False)
            )
        theme = TenantTheme(
            id=str(uuid.uuid4()), tenant_id=tenant_id, name=payload.name,
            is_default=payload.is_default, logo_url=payload.logo_url,
            favicon_url=payload.favicon_url, brand_name=payload.brand_name,
            tagline=payload.tagline, primary_color=payload.primary_color,
            secondary_color=payload.secondary_color, accent_color=payload.accent_color,
            background_color=payload.background_color, text_color=payload.text_color,
            error_color=payload.error_color, success_color=payload.success_color,
            font_family=payload.font_family, heading_font=payload.heading_font,
            border_radius=payload.border_radius, custom_css=payload.custom_css,
            email_header_html=payload.email_header_html,
            email_footer_html=payload.email_footer_html,
            assets=payload.assets or {},
        )
        self.db.add(theme)
        await self.db.commit()
        await self.db.refresh(theme)
        return theme

    async def add_custom_domain(self, tenant_id: str, domain: str) -> CustomDomain:
        await self.get_tenant(tenant_id)
        if not re.match(r"^([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}$", domain.lower()):
            raise ValidationError("Invalid domain format")
        existing = await self.db.execute(
            select(CustomDomain).where(CustomDomain.domain == domain.lower())
        )
        if existing.scalar_one_or_none():
            raise ConflictError(f"Domain '{domain}' is already registered")
        cd = CustomDomain(
            id=str(uuid.uuid4()), tenant_id=tenant_id, domain=domain.lower(),
            verification_token=f"faccp-verify-{secrets.token_hex(16)}",
            verified=False, ssl_status="pending",
        )
        self.db.add(cd)
        await self.db.commit()
        await self.db.refresh(cd)
        return cd

    async def verify_domain(self, domain_id: str, tenant_id: str) -> CustomDomain:
        result = await self.db.execute(
            select(CustomDomain).where(
                CustomDomain.id == domain_id, CustomDomain.tenant_id == tenant_id
            )
        )
        cd = result.scalar_one_or_none()
        if not cd:
            raise NotFoundError("Domain not found")
        cd.verified = True
        cd.verified_at = datetime.now(timezone.utc)
        cd.ssl_status = "active"
        await self.db.commit()
        return cd

    async def get_tenant_config(self, tenant_id: str, key: str) -> dict[str, Any] | None:
        result = await self.db.execute(
            select(TenantConfig).where(
                TenantConfig.tenant_id == tenant_id, TenantConfig.config_key == key
            )
        )
        c = result.scalar_one_or_none()
        return c.config_value if c else None

    async def set_tenant_config(self, tenant_id: str, payload: TenantConfigRequest) -> TenantConfig:
        await self.get_tenant(tenant_id)
        result = await self.db.execute(
            select(TenantConfig).where(
                TenantConfig.tenant_id == tenant_id, TenantConfig.config_key == payload.key
            )
        )
        config = result.scalar_one_or_none()
        if config is None:
            config = TenantConfig(
                id=str(uuid.uuid4()), tenant_id=tenant_id, config_key=payload.key,
                config_value=payload.value, is_sensitive=payload.is_sensitive,
            )
            self.db.add(config)
        else:
            config.config_value = payload.value
            config.is_sensitive = payload.is_sensitive
            config.version += 1
        await self.db.commit()
        return config

    async def resolve_tenant_by_domain(self, domain: str) -> Tenant | None:
        result = await self.db.execute(
            select(CustomDomain).where(
                CustomDomain.domain == domain.lower(),
                CustomDomain.verified.is_(True),
            )
        )
        cd = result.scalar_one_or_none()
        if not cd:
            return None
        return await self.get_tenant(cd.tenant_id)

    async def _get_tenant_by_code(self, code: str) -> Tenant | None:
        result = await self.db.execute(select(Tenant).where(Tenant.code == code))
        return result.scalar_one_or_none()
