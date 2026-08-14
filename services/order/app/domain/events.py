"""Domain events for Order service."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import ClassVar
from faccp_platform.events.contracts import DomainEvent


class OrderCreatedEvent(DomainEvent):
    event_type: ClassVar[str] = "order.created"
    order_id: str
    consumer_id: str
    total: str
    currency: str = "INR"
    compliance_decision_id: str | None = None
