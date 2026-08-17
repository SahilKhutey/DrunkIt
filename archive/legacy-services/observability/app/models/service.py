import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class ServiceHealth(Base):

    __tablename__ = "service_health_d14"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    service_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    latency_ms: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    error_rate: Mapped[float] = mapped_column(
        Float,
        default=0.0,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
