import uuid

from sqlalchemy import Float, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class ServiceSLO(Base):

    __tablename__ = "service_slos_d14"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    service: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    metric: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    target: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    window_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=30,
    )
