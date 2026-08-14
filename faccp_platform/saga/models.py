"""Saga instance database model."""

from __future__ import annotations

import uuid
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from faccp_platform.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from .enums import SagaState


class SagaInstance(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Tracks state and version for distributed saga orchestration."""

    __tablename__ = "saga_instances"

    order_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    state: Mapped[SagaState] = mapped_column(String(100), default=SagaState.CREATED, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    last_event_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
