from typing import Annotated
from fastapi import APIRouter, Depends, Header
from faccp_common.dto import SuccessResponse
from faccp_common.exceptions import UnauthorizedError
from faccp_common.security import decode_token
from app.api.dependencies import get_whitelabel_service
from app.config import get_settings
from app.schemas.whitelabel import (
    CreateTenantRequest, CreateThemeRequest, CustomDomainRequest,
    CustomDomainResponse, TenantConfigRequest, TenantResponse, ThemeResponse,
)
from app.services.whitelabel_service import WhiteLabelService

router = APIRouter(prefix="/whitelabel", tags=["White-Label"])
settings = get_settings()


def _auth(authorization: str | None = None, allow_public: bool = False) -> dict | None:
    if not authorization:
        if allow_public: return None
        raise UnauthorizedError("Authentication required")
    try:
        return decode_token(
            authorization.replace("Bearer ", "").strip(),
            secret=settings.jwt_secret,
            algorithm=settings.jwt_algorithm,
            issuer=settings.jwt_issuer,
            audience=settings.jwt_audience,
            expected_type="access",
        )
    except Exception as e:
        if allow_public: return None
        raise UnauthorizedError(f"Invalid token: {e}") from e


@router.post("/tenants", response_model=SuccessResponse[TenantResponse], status_code=201)
async def create_tenant(
    payload: CreateTenantRequest,
    service: Annotated[WhiteLabelService, Depends(get_whitelabel_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> SuccessResponse[TenantResponse]:
    _auth(authorization)
    t = await service.create_tenant(payload)
    return SuccessResponse(data=TenantResponse(
        id=t.id, code=t.code, name=t.name, legal_name=t.legal_name,
        primary_region=t.primary_region, allowed_regions=t.allowed_regions,
        is_active=t.is_active, subscription_tier=t.subscription_tier,
        feature_flags=t.feature_flags, created_at=t.created_at,
    ))


@router.get("/tenants/{tenant_id}", response_model=SuccessResponse[TenantResponse])
async def get_tenant(
    tenant_id: str,
    service: Annotated[WhiteLabelService, Depends(get_whitelabel_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> SuccessResponse[TenantResponse]:
    _auth(authorization)
    t = await service.get_tenant(tenant_id)
    return SuccessResponse(data=TenantResponse(
        id=t.id, code=t.code, name=t.name, legal_name=t.legal_name,
        primary_region=t.primary_region, allowed_regions=t.allowed_regions,
        is_active=t.is_active, subscription_tier=t.subscription_tier,
        feature_flags=t.feature_flags, created_at=t.created_at,
    ))


@router.get("/tenants/code/{code}", response_model=SuccessResponse[TenantResponse])
async def get_tenant_by_code(
    code: str,
    service: Annotated[WhiteLabelService, Depends(get_whitelabel_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> SuccessResponse[TenantResponse]:
    _auth(authorization)
    t = await service.get_tenant_by_code(code)
    return SuccessResponse(data=TenantResponse(
        id=t.id, code=t.code, name=t.name, legal_name=t.legal_name,
        primary_region=t.primary_region, allowed_regions=t.allowed_regions,
        is_active=t.is_active, subscription_tier=t.subscription_tier,
        feature_flags=t.feature_flags, created_at=t.created_at,
    ))


@router.post("/tenants/{tenant_id}/themes", response_model=SuccessResponse[ThemeResponse], status_code=201)
async def create_theme(
    tenant_id: str,
    payload: CreateThemeRequest,
    service: Annotated[WhiteLabelService, Depends(get_whitelabel_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> SuccessResponse[ThemeResponse]:
    _auth(authorization)
    th = await service.create_theme(tenant_id, payload)
    return SuccessResponse(data=ThemeResponse(
        id=th.id, tenant_id=th.tenant_id, name=th.name, is_default=th.is_default,
        brand_name=th.brand_name, tagline=th.tagline, logo_url=th.logo_url,
        favicon_url=th.favicon_url, primary_color=th.primary_color,
        secondary_color=th.secondary_color, accent_color=th.accent_color,
        background_color=th.background_color, text_color=th.text_color,
        error_color=th.error_color, success_color=th.success_color,
        font_family=th.font_family, border_radius=th.border_radius, custom_css=th.custom_css,
    ))


@router.post("/tenants/{tenant_id}/domains", response_model=SuccessResponse[CustomDomainResponse], status_code=201)
async def add_domain(
    tenant_id: str,
    payload: CustomDomainRequest,
    service: Annotated[WhiteLabelService, Depends(get_whitelabel_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> SuccessResponse[CustomDomainResponse]:
    _auth(authorization)
    d = await service.add_custom_domain(tenant_id, payload.domain)
    return SuccessResponse(data=CustomDomainResponse(
        id=d.id, domain=d.domain, is_primary=d.is_primary, verified=d.verified,
        verification_token=d.verification_token, ssl_status=d.ssl_status, verified_at=d.verified_at,
    ))


@router.post("/tenants/{tenant_id}/domains/{domain_id}/verify", response_model=SuccessResponse[CustomDomainResponse])
async def verify_domain(
    tenant_id: str,
    domain_id: str,
    service: Annotated[WhiteLabelService, Depends(get_whitelabel_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> SuccessResponse[CustomDomainResponse]:
    _auth(authorization)
    d = await service.verify_domain(domain_id, tenant_id)
    return SuccessResponse(data=CustomDomainResponse(
        id=d.id, domain=d.domain, is_primary=d.is_primary, verified=d.verified,
        verification_token=d.verification_token, ssl_status=d.ssl_status, verified_at=d.verified_at,
    ))


@router.put("/tenants/{tenant_id}/config", response_model=SuccessResponse[dict])
async def set_config(
    tenant_id: str,
    payload: TenantConfigRequest,
    service: Annotated[WhiteLabelService, Depends(get_whitelabel_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> SuccessResponse[dict]:
    _auth(authorization)
    c = await service.set_tenant_config(tenant_id, payload)
    return SuccessResponse(data={"key": c.config_key, "version": c.version})


@router.get("/resolve/{domain}", response_model=SuccessResponse[dict])
async def resolve_tenant(
    domain: str,
    service: Annotated[WhiteLabelService, Depends(get_whitelabel_service)],
) -> SuccessResponse[dict]:
    t = await service.resolve_tenant_by_domain(domain)
    if not t:
        return SuccessResponse(data={"tenant": None})
    return SuccessResponse(data={
        "tenant": {
            "id": t.id, "code": t.code, "name": t.name,
            "feature_flags": t.feature_flags, "subscription_tier": t.subscription_tier,
        }
    })
