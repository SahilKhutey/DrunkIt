from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, Field


class CreateTaskRequest(BaseModel):
    order_id: str


class VerifyHandoverRequest(BaseModel):
    order_id: str
    otp_code: str = Field(min_length=6, max_length=6)


class TaskResponse(BaseModel):
    id: str
    order_id: str
    driver_id: str | None
    status: str
    otp_code: str
    delivered_at: datetime | None
