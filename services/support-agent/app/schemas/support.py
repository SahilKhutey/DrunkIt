"""Support agent service API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SupportMessageRequest(BaseModel):
    conversation_id: str | None = None
    user_id: str
    content: str = Field(min_length=1)
    context: dict[str, Any] | None = None


class SupportMessageResponse(BaseModel):
    conversation_id: str
    message_id: str
    response: str
    citations: list[str]
    confidence: float
    requires_human: bool


class SupportTicketCreate(BaseModel):
    subject: str = Field(min_length=3, max_length=256)
    description: str = Field(min_length=3)
    priority: str = Field(default="NORMAL", pattern="^(LOW|NORMAL|HIGH|URGENT)$")


class SupportTicketResponse(BaseModel):
    id: str
    ticket_number: str
    subject: str
    description: str
    status: str
    priority: str
    created_at: datetime
