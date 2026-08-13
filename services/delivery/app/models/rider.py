import uuid

from sqlalchemy import Float, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class Rider(Base):

    __tablename__ = "riders_d11"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        index=True,
    )

    verification_status: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
    )

    current_latitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    current_longitude: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    active_delivery_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
    )
