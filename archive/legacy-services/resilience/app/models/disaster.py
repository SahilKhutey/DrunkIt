import uuid
from datetime import datetime

from sqlalchemy import DateTime, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class DisasterEvent(Base):

    __tablename__ = "disaster_events_d15"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    event_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    actor: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )

    metadata_json: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
