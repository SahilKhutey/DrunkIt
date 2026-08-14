import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class AuditEvent(Base):

    __tablename__ = "audit_events_d16"

    event_id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )

    sequence_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        unique=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    actor_type: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    actor_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    subject_type: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    subject_id: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    service: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    outcome: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    correlation_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    payload: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    previous_hash: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    event_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
