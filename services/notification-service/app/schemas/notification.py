from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field


class SendNotificationRequest(BaseModel):
    recipient: str
    channel: Literal["SMS", "EMAIL", "PUSH"] = "SMS"
    template_id: str
    variables: dict[str, str] = Field(default_factory=dict)


class SendNotificationResponse(BaseModel):
    message_id: str
    recipient: str
    channel: str
    status: str = "DELIVERED"
