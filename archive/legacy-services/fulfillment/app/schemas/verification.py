"""Delivery verification DTO schemas."""

from __future__ import annotations

import uuid
from pydantic import BaseModel, ConfigDict
from ..domain.enums import VerificationStatus


class VerificationResult(BaseModel):
    passed: bool
    method: str
    reference: str


class VerificationResponse(BaseModel):
    id: uuid.UUID
    delivery_id: uuid.UUID
    status: VerificationStatus
    verification_method: str | None = None
    verification_reference: str | None = None

    model_config = ConfigDict(from_attributes=True)
