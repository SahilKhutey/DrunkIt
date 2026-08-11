from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Literal

from pydantic import BaseModel, Field

ChannelSchema = Literal["email", "sms", "push", "in_app"]


class TemplateRequest(BaseModel):
    subject: str = ""
    body: str
    channel: ChannelSchema


class CampaignRequest(BaseModel):
    code: str = Field(min_length=2, max_length=64)
    name: str
    segment: str
    template: TemplateRequest
    status: Literal["draft", "scheduled", "active", "paused", "completed"] = "active"
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    frequency_cap_per_day: int = Field(default=1, gt=0)


class AudiencePlanRequest(BaseModel):
    campaign: CampaignRequest
    audience: list[dict[str, Any]]
    now: datetime | None = None


class ABTestRequest(BaseModel):
    experiment_code: str
    subject_id: str
    variants: dict[str, int]


class JourneyStepRequest(BaseModel):
    code: str
    template: TemplateRequest
    delay_seconds: int = Field(default=0, ge=0)
    exit_on_conversion: bool = True

    def delay(self) -> timedelta:
        return timedelta(seconds=self.delay_seconds)


class JourneyRequest(BaseModel):
    code: str
    name: str
    trigger_event: str
    status: Literal["draft", "scheduled", "active", "paused", "completed"] = "active"
    steps: list[JourneyStepRequest]


class JourneyScheduleRequest(BaseModel):
    journey: JourneyRequest
    profile_id: str
    triggered_at: datetime
