import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Integer, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class PolicyStatus(str, Enum):

    DRAFT = "DRAFT"

    REVIEW = "REVIEW"

    APPROVED = "APPROVED"

    SCHEDULED = "SCHEDULED"

    ACTIVE = "ACTIVE"

    RETIRED = "RETIRED"


class Policy(Base):

    __tablename__ = "policies_d16"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    policy_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="DRAFT",
    )

    jurisdiction: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    scope: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    rules: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    effective_from: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    effective_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
