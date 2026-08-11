from __future__ import annotations

from datetime import date, datetime
from typing import Any
from pydantic import BaseModel, Field


class ProfileCreateRequest(BaseModel):
    account_id: str
    full_name: str
    date_of_birth: date
    state_code: str
    delivery_address: dict[str, Any] | None = None


class ProfileResponse(BaseModel):
    id: str
    account_id: str
    full_name: str
    date_of_birth: date
    verification_level: str
    age_eligible: bool
    state_code: str
    default_delivery_address: dict[str, Any] | None
    created_at: datetime


class ZKAgeClaimRequest(BaseModel):
    consumer_id: str
    target_state: str


class ZKAgeClaimResponse(BaseModel):
    consumer_id: str
    target_state: str
    age_eligible: bool
    verification_level: str
    proof_token: str
