import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class BackupRecord(Base):

    __tablename__ = "backup_records_d15"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    backup_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
    )

    resource: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    backup_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="FULL",
    )

    location: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )

    checksum: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    size_bytes: Mapped[int] = mapped_column(
        Integer,
        default=0,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
