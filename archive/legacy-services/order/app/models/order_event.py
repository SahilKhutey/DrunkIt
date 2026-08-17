import uuid
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class OrderEvent(Base):

    __tablename__ = "order_events_d9"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    previous_status: Mapped[str | None] = mapped_column(
        String(40),
        nullable=True,
    )

    new_status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    actor_type: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="CUSTOMER",
    )

    actor_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
