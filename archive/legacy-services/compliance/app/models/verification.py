import uuid
from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class VerificationType:
    IDENTITY = "IDENTITY"
    AGE_ELIGIBILITY = "AGE_ELIGIBILITY"
    ADDRESS = "ADDRESS"
    RETAILER_BUSINESS = "RETAILER_BUSINESS"
    RETAILER_LICENCE = "RETAILER_LICENCE"
    DRIVER_IDENTITY = "DRIVER_IDENTITY"
    DRIVER_ELIGIBILITY = "DRIVER_ELIGIBILITY"
    PERMIT = "PERMIT"


class VerificationStatus:
    PENDING = "PENDING"
    IN_REVIEW = "IN_REVIEW"
    VERIFIED = "VERIFIED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"
    FAILED = "FAILED"
    SUSPENDED = "SUSPENDED"


class Verification(Base):

    __tablename__ = "verifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    identity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    verification_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    jurisdiction: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    reference_id: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )
