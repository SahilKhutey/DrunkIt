import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class ReconciliationRecord(Base):

    __tablename__ = "reconciliation_records_d10"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    provider: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    provider_reference: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    internal_reference: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    provider_amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    internal_amount: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
