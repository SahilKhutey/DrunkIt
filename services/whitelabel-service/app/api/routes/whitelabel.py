"""Whitelabel API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from faccp_common.dto import SuccessResponse

from app.api.dependencies import get_whitelabel_service
from app.schemas.whitelabel import (
    DomainBindingCreate, DomainBindingResponse, TenantBrandingCreate,
    TenantBrandingResponse,
)
from app.services.whitelabel_service import WhitelabelService

router = APIRouter(prefix="/whitelabel", tags=["Multi-Tenant Portal Engine"])


@router.post("/branding", response_model=SuccessResponse[TenantBrandingResponse], status_code=201)
async def update_branding(
    payload: TenantBrandingCreate,
    service: Annotated[WhitelabelService, Depends(get_whitelabel_service)],
) -> SuccessResponse[TenantBrandingResponse]:
    branding = await service.update_branding(payload)
    return SuccessResponse(data=TenantBrandingResponse(
        id=branding.id, tenant_id=branding.tenant_id, brand_name=branding.brand_name,
        logo_url=branding.logo_url, primary_color_hex=branding.primary_color_hex,
        secondary_color_hex=branding.secondary_color_hex, updated_at=branding.updated_at,
    ), message="Tenant branding configuration updated")


@router.get("/branding/{tenant_id}", response_model=SuccessResponse[TenantBrandingResponse])
async def get_branding(
    tenant_id: str,
    service: Annotated[WhitelabelService, Depends(get_whitelabel_service)],
) -> SuccessResponse[TenantBrandingResponse]:
    branding = await service.get_branding(tenant_id)
    return SuccessResponse(data=TenantBrandingResponse(
        id=branding.id, tenant_id=branding.tenant_id, brand_name=branding.brand_name,
        logo_url=branding.logo_url, primary_color_hex=branding.primary_color_hex,
        secondary_color_hex=branding.secondary_color_hex, updated_at=branding.updated_at,
    ))


@router.post("/domains", response_model=SuccessResponse[DomainBindingResponse], status_code=201)
async def bind_domain(
    payload: DomainBindingCreate,
    service: Annotated[WhitelabelService, Depends(get_whitelabel_service)],
) -> SuccessResponse[DomainBindingResponse]:
    binding = await service.bind_domain(payload)
    return SuccessResponse(data=DomainBindingResponse(
        id=binding.id, tenant_id=binding.tenant_id, domain_name=binding.domain_name,
        ssl_certified=binding.ssl_certified, status=binding.status, created_at=binding.created_at,
    ), message="Custom domain binding registered")
