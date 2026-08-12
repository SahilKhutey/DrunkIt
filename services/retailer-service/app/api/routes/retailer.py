"""Retailer API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from faccp_common.dto import SuccessResponse

from app.api.dependencies import get_retailer_service
from app.schemas.retailer import (
    LicenseCreate, LicenseResponse, OrganizationCreate, OrganizationResponse,
    StaffAssignCreate, StaffAssignResponse, StoreCreate, StoreResponse,
)
from app.services.retailer_service import RetailerService

router = APIRouter(prefix="/retailer", tags=["Retailer Engine"])


@router.post("/organizations", response_model=SuccessResponse[OrganizationResponse], status_code=201)
async def create_organization(
    payload: OrganizationCreate,
    service: Annotated[RetailerService, Depends(get_retailer_service)],
) -> SuccessResponse[OrganizationResponse]:
    org = await service.create_organization(payload)
    return SuccessResponse(data=OrganizationResponse(
        id=org.id, legal_name=org.legal_name, trade_name=org.trade_name,
        business_type=org.business_type, gstin=org.gstin, pan=org.pan,
        owner_user_id=org.owner_user_id, seller_level=org.seller_level,
        is_active=org.is_active, is_verified=org.is_verified,
        created_at=org.created_at,
    ), message="Organization registered")


@router.get("/organizations/{org_id}", response_model=SuccessResponse[OrganizationResponse])
async def get_organization(
    org_id: str,
    service: Annotated[RetailerService, Depends(get_retailer_service)],
) -> SuccessResponse[OrganizationResponse]:
    org = await service.get_organization(org_id)
    return SuccessResponse(data=OrganizationResponse(
        id=org.id, legal_name=org.legal_name, trade_name=org.trade_name,
        business_type=org.business_type, gstin=org.gstin, pan=org.pan,
        owner_user_id=org.owner_user_id, seller_level=org.seller_level,
        is_active=org.is_active, is_verified=org.is_verified,
        created_at=org.created_at,
    ))


@router.post("/stores", response_model=SuccessResponse[StoreResponse], status_code=201)
async def create_store(
    payload: StoreCreate,
    service: Annotated[RetailerService, Depends(get_retailer_service)],
) -> SuccessResponse[StoreResponse]:
    store = await service.create_store(payload)
    return SuccessResponse(data=StoreResponse(
        id=store.id, organization_id=store.organization_id, code=store.code,
        name=store.name, store_type=store.store_type, address_line_1=store.address_line_1,
        address_line_2=store.address_line_2, city=store.city, state=store.state,
        pincode=store.pincode, jurisdiction=store.jurisdiction,
        latitude=store.latitude, longitude=store.longitude,
        is_active=store.is_active, is_accepting_orders=store.is_accepting_orders,
        created_at=store.created_at,
    ), message="Store location created")


@router.get("/stores/{store_id}", response_model=SuccessResponse[StoreResponse])
async def get_store(
    store_id: str,
    service: Annotated[RetailerService, Depends(get_retailer_service)],
) -> SuccessResponse[StoreResponse]:
    store = await service.get_store(store_id)
    return SuccessResponse(data=StoreResponse(
        id=store.id, organization_id=store.organization_id, code=store.code,
        name=store.name, store_type=store.store_type, address_line_1=store.address_line_1,
        address_line_2=store.address_line_2, city=store.city, state=store.state,
        pincode=store.pincode, jurisdiction=store.jurisdiction,
        latitude=store.latitude, longitude=store.longitude,
        is_active=store.is_active, is_accepting_orders=store.is_accepting_orders,
        created_at=store.created_at,
    ))


@router.get("/organizations/{org_id}/stores", response_model=SuccessResponse[list[StoreResponse]])
async def list_org_stores(
    org_id: str,
    service: Annotated[RetailerService, Depends(get_retailer_service)],
) -> SuccessResponse[list[StoreResponse]]:
    stores = await service.list_stores_for_org(org_id)
    return SuccessResponse(data=[StoreResponse(
        id=s.id, organization_id=s.organization_id, code=s.code, name=s.name,
        store_type=s.store_type, address_line_1=s.address_line_1,
        address_line_2=s.address_line_2, city=s.city, state=s.state,
        pincode=s.pincode, jurisdiction=s.jurisdiction,
        latitude=s.latitude, longitude=s.longitude,
        is_active=s.is_active, is_accepting_orders=s.is_accepting_orders,
        created_at=s.created_at,
    ) for s in stores])


@router.post("/stores/{store_id}/licenses", response_model=SuccessResponse[LicenseResponse], status_code=201)
async def add_license(
    store_id: str,
    payload: LicenseCreate,
    service: Annotated[RetailerService, Depends(get_retailer_service)],
) -> SuccessResponse[LicenseResponse]:
    lic = await service.add_store_license(store_id, payload)
    return SuccessResponse(data=LicenseResponse(
        id=lic.id, store_id=lic.store_id, license_number=lic.license_number,
        license_type=lic.license_type, issuing_authority=lic.issuing_authority,
        jurisdiction=lic.jurisdiction, valid_from=lic.valid_from, valid_until=lic.valid_until,
        status=lic.status, document_url=lic.document_url, created_at=lic.created_at,
    ), message="Store license added")


@router.get("/stores/{store_id}/licenses", response_model=SuccessResponse[list[LicenseResponse]])
async def list_licenses(
    store_id: str,
    service: Annotated[RetailerService, Depends(get_retailer_service)],
) -> SuccessResponse[list[LicenseResponse]]:
    licenses = await service.list_store_licenses(store_id)
    return SuccessResponse(data=[LicenseResponse(
        id=l.id, store_id=l.store_id, license_number=l.license_number,
        license_type=l.license_type, issuing_authority=l.issuing_authority,
        jurisdiction=l.jurisdiction, valid_from=l.valid_from, valid_until=l.valid_until,
        status=l.status, document_url=l.document_url, created_at=l.created_at,
    ) for l in licenses])


@router.post("/stores/{store_id}/staff", response_model=SuccessResponse[StaffAssignResponse], status_code=201)
async def assign_staff(
    store_id: str,
    payload: StaffAssignCreate,
    service: Annotated[RetailerService, Depends(get_retailer_service)],
) -> SuccessResponse[StaffAssignResponse]:
    st = await service.assign_staff(store_id, payload)
    return SuccessResponse(data=StaffAssignResponse(
        id=st.id, store_id=st.store_id, user_id=st.user_id,
        role_in_store=st.role_in_store, is_active=st.is_active,
        created_at=st.created_at,
    ), message="Staff assigned to store")


@router.get("/stores/{store_id}/staff", response_model=SuccessResponse[list[StaffAssignResponse]])
async def list_staff(
    store_id: str,
    service: Annotated[RetailerService, Depends(get_retailer_service)],
) -> SuccessResponse[list[StaffAssignResponse]]:
    staff_list = await service.list_store_staff(store_id)
    return SuccessResponse(data=[StaffAssignResponse(
        id=st.id, store_id=st.store_id, user_id=st.user_id,
        role_in_store=st.role_in_store, is_active=st.is_active,
        created_at=st.created_at,
    ) for st in staff_list])
