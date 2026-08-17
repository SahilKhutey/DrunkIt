import uuid

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class Retailer(Base):

    __tablename__ = "compliance_retailers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    legal_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    display_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    jurisdiction: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    compliance_status: Mapped[str] = mapped_column(
        String(50),
        default="PENDING",
        nullable=False,
    )
