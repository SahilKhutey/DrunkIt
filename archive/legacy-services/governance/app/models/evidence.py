import uuid
from datetime import datetime

from sqlalchemy import DateTime, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class EvidenceRecord(Base):

    __tablename__ = "evidence_records_d16"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    evidence_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    evidence_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    subject_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    subject_id: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    external_reference: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
