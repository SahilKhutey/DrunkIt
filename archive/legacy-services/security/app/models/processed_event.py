from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class ProcessedEvent(Base):

    __tablename__ = "processed_security_events_d13"

    event_id: Mapped[str] = mapped_column(
        String(200),
        primary_key=True,
    )

    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
