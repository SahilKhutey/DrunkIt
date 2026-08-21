"""Pydantic schemas for deterministic compliance checks, decisions, and regulatory policies."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ComplianceCheckRequest(BaseModel):
    """Input payload for regulatory and policy evaluation."""

    correlation_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique correlation ID for audit tracing")
    jurisdiction_code: str = Field(min_length=2, max_length=10, description="State code, e.g., 'IN-WB', 'WB', 'IN-MH'")
    consumer_id: uuid.UUID | None = None
    consumer_age: int | None = Field(default=None, ge=0, le=120)
    is_age_verified: bool = False
    retailer_id: uuid.UUID | None = None
    retailer_location_id: uuid.UUID | None = None
    product_id: uuid.UUID | None = None
    sku_id: uuid.UUID | None = None
    product_class: str = Field(default="SPIRITS", description="SPIRITS, BEER, WINE, RTD")
    channel: str = Field(default="ONLINE_ORDER", description="ONLINE_ORDER, IN_STORE, HOME_DELIVERY")
    quantity: int = Field(default=1, gt=0)
    total_volume_ml: int = Field(default=750, gt=0)
    current_time: datetime | None = None
    extra_context: dict[str, Any] = Field(default_factory=dict)


class ComplianceDecisionResponse(BaseModel):
    """Deterministic output decision of the compliance engine."""

    check_id: uuid.UUID
    correlation_id: uuid.UUID
    jurisdiction_code: str
    decision: str = Field(description="ALLOWED, DENIED, or REQUIRES_VERIFICATION")
    reason_codes: list[str] = Field(default_factory=list)
    required_checks: list[str] = Field(default_factory=list)
    rule_set_version: str
    decided_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JurisdictionPolicySummary(BaseModel):
    """Summary of a jurisdiction's active alcohol regulations."""

    jurisdiction_code: str
    jurisdiction_name: str
    version: str
    legal_drinking_age: dict[str, int]
    channels: dict[str, Any]
    operating_hours: dict[str, str]
    possession_limits_ml: dict[str, int]
    dry_days_count: int
