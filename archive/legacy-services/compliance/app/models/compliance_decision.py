import uuid
from datetime import datetime

from sqlalchemy import DateTime, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class ComplianceDecision(Base):

    __tablename__ = "compliance_decisions_d12"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    subject_type: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    subject_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    operation: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    jurisdiction_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    decision: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    policy_version: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    reasons: Mapped[list] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
