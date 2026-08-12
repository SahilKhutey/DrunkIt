"""Consumer service API schemas."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field


class ConsumerProfileCreate(BaseModel):
    user_id: str
    first_name: str = Field(min_length=1, max_length=64)
    last_name: str = Field(min_length=1, max_length=64)
    display_name: str | None = None
    date_of_birth: date | None = None
    primary_jurisdiction: str = "IN-KA"
    preferred_language: str = "en"


class ConsumerProfileResponse(BaseModel):
    id: str
    user_id: str
    first_name: str
    last_name: str
    display_name: str | None
    date_of_birth: date | None
    consumer_level: str
    is_age_verified: bool
    age_verified_at: datetime | None
    kyc_status: str
    primary_jurisdiction: str
    trust_score: int
    created_at: datetime


class AddressCreate(BaseModel):
    label: str = Field(default="Home", max_length=32)
    recipient_name: str = Field(min_length=1, max_length=128)
    recipient_phone: str = Field(min_length=10, max_length=15)
    address_line_1: str = Field(min_length=3, max_length=255)
    address_line_2: str | None = None
    landmark: str | None = None
    city: str = Field(min_length=2, max_length=64)
    state: str = Field(min_length=2, max_length=64)
    pincode: str = Field(min_length=6, max_length=16)
    jurisdiction: str = Field(min_length=2, max_length=64)
    latitude: float
    longitude: float
    is_default: bool = False
    delivery_instructions: str | None = None


class AddressResponse(BaseModel):
    id: str
    consumer_id: str
    label: str
    recipient_name: str
    recipient_phone: str
    address_line_1: str
    address_line_2: str | None
    landmark: str | None
    city: str
    state: str
    pincode: str
    jurisdiction: str
    latitude: float
    longitude: float
    is_default: bool
    delivery_instructions: str | None


class AgeVerificationSubmit(BaseModel):
    verification_type: str = "AADHAAR_OKYC"
    document_type: str = "AADHAAR"
    document_number: str = Field(min_length=4, max_length=64)
    date_of_birth: date
    verifier_provider: str = "SUREPASS_API"


class AgeVerificationResponse(BaseModel):
    id: str
    consumer_id: str
    verification_type: str
    document_type: str
    verified_age: int
    verification_status: str
    verified_at: datetime
