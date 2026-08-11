from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class CreateAPIKeyRequest(BaseModel):
    app_id: str = Field(min_length=3, max_length=128)
    environment: Literal["sandbox", "production"] = "sandbox"


class APIKeyResponse(BaseModel):
    key_id: str
    plaintext_key: str
    key_hash: str
    prefix: str
    created_at: datetime


class PlanLimitRequest(BaseModel):
    requests_per_minute: int = Field(gt=0)
    requests_per_day: int = Field(gt=0)
    requests_per_month: int = Field(gt=0)
    burst: int = Field(default=0, ge=0)


class CreateSubscriptionRequest(BaseModel):
    developer_id: str
    app_id: str
    product_code: str
    plan_code: str = "starter"
    monthly_price: Decimal = Decimal("0")
    currency: str = "INR"
    limits: PlanLimitRequest = Field(
        default_factory=lambda: PlanLimitRequest(
            requests_per_minute=60,
            requests_per_day=10_000,
            requests_per_month=250_000,
        )
    )


class UsageEventRequest(BaseModel):
    app_id: str
    product_code: str
    endpoint: str
    status_code: int = Field(ge=100, le=599)
    latency_ms: int = Field(ge=0)
    occurred_at: datetime | None = None


class UsageDecisionRequest(BaseModel):
    app_id: str
    product_code: str
    window: Literal["minute", "day", "month"] = "minute"
    window_start: datetime
    now: datetime | None = None
