import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class SKU(Base):

    __tablename__ = "catalogue_skus"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    sku_code: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        nullable=False,
    )

    barcode: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
    )

    volume_ml: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    packaging_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    strength_value: Mapped[float | None] = mapped_column(
        Numeric(8, 3),
        nullable=True,
    )

    strength_unit: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
