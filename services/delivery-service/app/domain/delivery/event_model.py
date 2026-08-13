import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class DeliveryEvent(Base):
    __tablename__ = "delivery_events"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    delivery_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    actor_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    actor_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    payload: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="{}",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
