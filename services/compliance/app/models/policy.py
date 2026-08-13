import uuid

from sqlalchemy import JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class CompliancePolicy(Base):

    __tablename__ = "compliance_policies_d12"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    policy_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    jurisdiction_id: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    version: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    rules: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )
