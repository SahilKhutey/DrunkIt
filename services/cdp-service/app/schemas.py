from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field

ConsentScopeSchema = Literal["analytics", "personalization", "marketing", "third_party_export"]


class ResolveProfileRequest(BaseModel):
    identifiers: dict[str, str] = Field(min_length=1)
    traits: dict[str, Any] = Field(default_factory=dict)


class EventRequest(BaseModel):
    profile_id: str
    event_type: str
    occurred_at: datetime
    properties: dict[str, Any] = Field(default_factory=dict)
    value: Decimal = Decimal("0")


class ConsentRequest(BaseModel):
    profile_id: str
    scopes: set[ConsentScopeSchema]


class AudienceRequest(BaseModel):
    segment: Literal[
        "new_customer",
        "high_value",
        "at_risk",
        "loyal",
        "dormant",
        "discount_sensitive",
    ]
    consent_scope: ConsentScopeSchema = "marketing"
    now: datetime | None = None
