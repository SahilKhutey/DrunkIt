from typing import Annotated, Any

from fastapi import APIRouter, Depends

from faccp_common.dto import APIResponse

from app.api.dependencies import get_whitelabel_service
from app.schemas.whitelabel import (
    CreateTenantRequest,
    CreateThemeRequest,
    CustomDomainRequest,
    CustomDomainResponse,
    TenantConfigRequest,
    TenantResponse,
    ThemeResponse,
    VerifyDomainResponse,
)
from app.services.whitelabel_service import WhiteLabelService

router = APIRouter(prefix="/whitelabel", tags=["White Label"])


def _tenant_response(tenant: Any) -> TenantResponse:
    return TenantResponse(
        id=tenant.id,
        code=tenant.code,
        name=tenant.name,
        legal_name=tenant.legal_name,
        primary_region=tenant.primary_region,
        allowed_regions=tenant.allowed_regions,
        is_active=tenant.is_active,
        subscription_tier=tenant.subscription_tier,
        feature_flags=tenant.feature_flags,
        created_at=tenant.created_at,
    )


def _theme_response(theme: Any) -> ThemeResponse:
    return ThemeResponse(
        id=theme.id,
        tenant_id=theme.tenant_id,
        name=theme.name,
        is_default=theme.is_default,
        brand_name=theme.brand_name,
        tagline=theme.tagline,
        logo_url=theme.logo_url,
        favicon_url=theme.favicon_url,
        primary_color=theme.primary_color,
        secondary_color=theme.secondary_color,
        accent_color=theme.accent_color,
        background_color=theme.background_color,
        text_color=theme.text_color,
        error_color=theme.error_color,
        success_color=theme.success_color,
        font_family=theme.font_family,
        border_radius=theme.border_radius,
        custom_css=theme.custom_css,
    )


def _domain_response(domain: Any) -> CustomDomainResponse:
    return CustomDomainResponse(
        id=domain.id,
        domain=domain.domain,
        is_primary=domain.is_primary,
        verified=domain.verified,
        verification_token=domain.verification_token,
        ssl_status=domain.ssl_status,
        verified_at=domain.verified_at,
    )


@router.post("/tenants", status_code=201)
async def create_tenant(
    payload: CreateTenantRequest,
    service: Annotated[WhiteLabelService, Depends(get_whitelabel_service)],
) -> APIResponse[TenantResponse]:
    tenant = await service.create_tenant(payload)
    return APIResponse(data=_tenant_response(tenant))


@router.get("/tenants/code/{code}")
async def get_tenant_by_code(
    code: str,
    service: Annotated[WhiteLabelService, Depends(get_whitelabel_service)],
) -> APIResponse[TenantResponse]:
    tenant = await service.get_tenant_by_code(code)
    return APIResponse(data=_tenant_response(tenant))


@router.get("/tenants/{tenant_id}")
async def get_tenant(
    tenant_id: str,
    service: Annotated[WhiteLabelService, Depends(get_whitelabel_service)],
) -> APIResponse[TenantResponse]:
    tenant = await service.get_tenant(tenant_id)
    return APIResponse(data=_tenant_response(tenant))


@router.post("/tenants/{tenant_id}/themes", status_code=201)
async def create_theme(
    tenant_id: str,
    payload: CreateThemeRequest,
    service: Annotated[WhiteLabelService, Depends(get_whitelabel_service)],
) -> APIResponse[ThemeResponse]:
    theme = await service.create_theme(tenant_id, payload)
    return APIResponse(data=_theme_response(theme))


@router.post("/tenants/{tenant_id}/domains", status_code=201)
async def add_custom_domain(
    tenant_id: str,
    payload: CustomDomainRequest,
    service: Annotated[WhiteLabelService, Depends(get_whitelabel_service)],
) -> APIResponse[CustomDomainResponse]:
    domain = await service.add_custom_domain(tenant_id, payload.domain)
    return APIResponse(data=_domain_response(domain))


@router.post("/tenants/{tenant_id}/domains/{domain_id}/verify")
async def verify_domain(
    tenant_id: str,
    domain_id: str,
    service: Annotated[WhiteLabelService, Depends(get_whitelabel_service)],
) -> APIResponse[VerifyDomainResponse]:
    domain = await service.verify_domain(domain_id, tenant_id)
    return APIResponse(
        data=VerifyDomainResponse(
            id=domain.id,
            domain=domain.domain,
            verified=domain.verified,
            ssl_status=domain.ssl_status,
        )
    )


@router.get("/domains/{domain}/tenant")
async def resolve_tenant_by_domain(
    domain: str,
    service: Annotated[WhiteLabelService, Depends(get_whitelabel_service)],
) -> APIResponse[TenantResponse | None]:
    tenant = await service.resolve_tenant_by_domain(domain)
    return APIResponse(data=_tenant_response(tenant) if tenant else None)


@router.put("/tenants/{tenant_id}/configs")
async def set_tenant_config(
    tenant_id: str,
    payload: TenantConfigRequest,
    service: Annotated[WhiteLabelService, Depends(get_whitelabel_service)],
) -> APIResponse[dict[str, Any]]:
    config = await service.set_tenant_config(tenant_id, payload)
    return APIResponse(
        data={
            "id": config.id,
            "tenant_id": config.tenant_id,
            "key": config.config_key,
            "value": {} if config.is_sensitive else config.config_value,
            "is_sensitive": config.is_sensitive,
            "version": config.version,
        }
    )


@router.get("/tenants/{tenant_id}/configs/{key}")
async def get_tenant_config(
    tenant_id: str,
    key: str,
    service: Annotated[WhiteLabelService, Depends(get_whitelabel_service)],
) -> APIResponse[dict[str, Any] | None]:
    config = await service.get_tenant_config(tenant_id, key)
    return APIResponse(data=config)
