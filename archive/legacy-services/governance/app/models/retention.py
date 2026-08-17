import uuid

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class RetentionPolicy(Base):

    __tablename__ = "retention_policies_d16"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    resource_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    retention_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=365,
    )

    archive_after_days: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    deletion_allowed: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
