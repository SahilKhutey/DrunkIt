"""Consumer profile schemas."""

from __future__ import annotations

from datetime import date
from pydantic import BaseModel, Field


class ProfileUpdate(BaseModel):
    first_name: str | None = Field(default=None, max_length=100)
    last_name: str | None = Field(default=None, max_length=100)
    date_of_birth: date | None = None
    preferences: dict = Field(default_factory=dict)


class ProfileResponse(ProfileUpdate):
    consumer_id: str
