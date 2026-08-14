"""Consumer schemas for request and response DTOs."""

from __future__ import annotations

import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ConsumerCreate(BaseModel):
    identity_id: uuid.UUID


class ConsumerResponse(BaseModel):
    id: uuid.UUID
    identity_id: uuid.UUID
    status: str
    version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
