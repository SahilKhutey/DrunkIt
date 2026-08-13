import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class Jurisdiction(Base):

    __tablename__ = "jurisdictions_d12"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    country_code: Mapped[str] = mapped_column(
        String(5),
        nullable=False,
    )

    state_code: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    district_code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )
