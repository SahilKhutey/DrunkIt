import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    String,
)

from sqlalchemy.dialects.postgresql import (
    JSONB,
    UUID,
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
)

from packages.database.base import Base


class AuditLog(Base):

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    actor_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    actor_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    resource_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    resource_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    metadata: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
