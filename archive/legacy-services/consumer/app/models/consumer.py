"""Consumer entity database model."""

from __future__ import annotations

import uuid
from datetime import datetime
from sqlalchemy import DateTime, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from faccp_platform.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from ..domain.enums import ConsumerStatus


class Consumer(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Consumer root aggregate entity model."""

    __tablename__ = "consumers"

    identity_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, nullable=False)
    status: Mapped[ConsumerStatus] = mapped_column(
        Enum(ConsumerStatus, name="consumer_status"),
        default=ConsumerStatus.PENDING,
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
