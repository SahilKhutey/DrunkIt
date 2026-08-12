"""Realtime service API schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class BroadcastMessageRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=64)
    channel_id: str
    event_type: str
    data: dict


class ConnectionStatsResponse(BaseModel):
    active_channels: int
    total_connections: int
