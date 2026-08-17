"""Policy schemas."""

from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from ..domain.enums import PolicyStatus


class PolicyCreate(BaseModel):
    jurisdiction_id: uuid.UUID
    name: str = Field(max_length=255)
    version: str = Field(default="1.0.0", max_length=50)
    effective_from: datetime | None = None
    effective_until: datetime | None = None
    status: PolicyStatus = PolicyStatus.DRAFT


class PolicyResponse(PolicyCreate):
    id: uuid.UUID
    status: PolicyStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
