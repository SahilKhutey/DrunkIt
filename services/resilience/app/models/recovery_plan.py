import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class RecoveryPlan(Base):

    __tablename__ = "recovery_plans_d15"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    service: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    rpo_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
    )

    rto_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=15,
    )

    priority: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="P1",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
