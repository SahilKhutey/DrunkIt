import uuid
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class SecurityActionModel(Base):

    __tablename__ = "security_actions_d13"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    subject_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    subject_id: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
