"""Consumer API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status

from faccp_common.dto import SuccessResponse

from app.api.dependencies import get_consumer_service
from app.schemas.consumer import (
    AddressCreate, AddressResponse, AgeVerificationResponse, AgeVerificationSubmit,
    ConsumerProfileCreate, ConsumerProfileResponse,
)
from app.services.consumer_service import ConsumerService

router = APIRouter(prefix="/consumer", tags=["Consumer Engine"])


@router.post("/profile", response_model=SuccessResponse[ConsumerProfileResponse], status_code=201)
async def create_profile(
    payload: ConsumerProfileCreate,
    service: Annotated[ConsumerService, Depends(get_consumer_service)],
) -> SuccessResponse[ConsumerProfileResponse]:
    p = await service.create_profile(payload)
    return SuccessResponse(data=ConsumerProfileResponse(
        id=p.id, user_id=p.user_id, first_name=p.first_name, last_name=p.last_name,
        display_name=p.display_name, date_of_birth=p.date_of_birth,
        consumer_level=p.consumer_level, is_age_verified=p.is_age_verified,
        age_verified_at=p.age_verified_at, kyc_status=p.kyc_status,
        primary_jurisdiction=p.primary_jurisdiction, trust_score=p.trust_score,
        created_at=p.created_at,
    ), message="Profile created successfully")


@router.get("/profile/{consumer_id}", response_model=SuccessResponse[ConsumerProfileResponse])
async def get_profile(
    consumer_id: str,
    service: Annotated[ConsumerService, Depends(get_consumer_service)],
) -> SuccessResponse[ConsumerProfileResponse]:
    p = await service.get_profile(consumer_id)
    return SuccessResponse(data=ConsumerProfileResponse(
        id=p.id, user_id=p.user_id, first_name=p.first_name, last_name=p.last_name,
        display_name=p.display_name, date_of_birth=p.date_of_birth,
        consumer_level=p.consumer_level, is_age_verified=p.is_age_verified,
        age_verified_at=p.age_verified_at, kyc_status=p.kyc_status,
        primary_jurisdiction=p.primary_jurisdiction, trust_score=p.trust_score,
        created_at=p.created_at,
    ))


@router.post("/profile/{consumer_id}/addresses", response_model=SuccessResponse[AddressResponse], status_code=201)
async def add_address(
    consumer_id: str,
    payload: AddressCreate,
    service: Annotated[ConsumerService, Depends(get_consumer_service)],
) -> SuccessResponse[AddressResponse]:
    addr = await service.add_address(consumer_id, payload)
    return SuccessResponse(data=AddressResponse(
        id=addr.id, consumer_id=addr.consumer_id, label=addr.label,
        recipient_name=addr.recipient_name, recipient_phone=addr.recipient_phone,
        address_line_1=addr.address_line_1, address_line_2=addr.address_line_2,
        landmark=addr.landmark, city=addr.city, state=addr.state, pincode=addr.pincode,
        jurisdiction=addr.jurisdiction, latitude=addr.latitude, longitude=addr.longitude,
        is_default=addr.is_default, delivery_instructions=addr.delivery_instructions,
    ), message="Address added successfully")


@router.get("/profile/{consumer_id}/addresses", response_model=SuccessResponse[list[AddressResponse]])
async def list_addresses(
    consumer_id: str,
    service: Annotated[ConsumerService, Depends(get_consumer_service)],
) -> SuccessResponse[list[AddressResponse]]:
    addresses = await service.list_addresses(consumer_id)
    return SuccessResponse(data=[AddressResponse(
        id=a.id, consumer_id=a.consumer_id, label=a.label,
        recipient_name=a.recipient_name, recipient_phone=a.recipient_phone,
        address_line_1=a.address_line_1, address_line_2=a.address_line_2,
        landmark=a.landmark, city=a.city, state=a.state, pincode=a.pincode,
        jurisdiction=a.jurisdiction, latitude=a.latitude, longitude=a.longitude,
        is_default=a.is_default, delivery_instructions=a.delivery_instructions,
    ) for a in addresses])


@router.delete("/profile/{consumer_id}/addresses/{address_id}", response_model=SuccessResponse[None])
async def delete_address(
    consumer_id: str,
    address_id: str,
    service: Annotated[ConsumerService, Depends(get_consumer_service)],
) -> SuccessResponse[None]:
    await service.delete_address(consumer_id, address_id)
    return SuccessResponse(data=None, message="Address deleted")


@router.post("/profile/{consumer_id}/age-verification", response_model=SuccessResponse[AgeVerificationResponse])
async def verify_age(
    consumer_id: str,
    payload: AgeVerificationSubmit,
    service: Annotated[ConsumerService, Depends(get_consumer_service)],
) -> SuccessResponse[AgeVerificationResponse]:
    rec = await service.submit_age_verification(consumer_id, payload)
    return SuccessResponse(data=AgeVerificationResponse(
        id=rec.id, consumer_id=rec.consumer_id, verification_type=rec.verification_type,
        document_type=rec.document_type, verified_age=rec.verified_age,
        verification_status=rec.verification_status, verified_at=rec.verified_at,
    ), message="Age verification evaluated")
