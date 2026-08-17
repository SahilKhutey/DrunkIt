import uuid
from datetime import datetime

from sqlalchemy import DateTime, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class SecurityAuditEvent(Base):

    __tablename__ = "security_audit_events_d13"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    actor_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    actor_id: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    subject_id: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    metadata_json: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
