"""Jurisdiction schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class JurisdictionCreate(BaseModel):
    country_code: str = Field(min_length=2, max_length=2)
    state_code: str | None = Field(default=None, max_length=20)


class JurisdictionResponse(JurisdictionCreate):
    id: uuid.UUID
    active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
