import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from packages.database.base import Base


class Inventory(Base):

    __tablename__ = "inventory_items"

    __table_args__ = (
        UniqueConstraint(
            "store_id",
            "sku_id",
            name="uq_store_sku_inventory",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    store_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    sku_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    on_hand: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    reserved: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    damaged: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    blocked: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    @property
    def available(self) -> int:
        return max(
            0,
            self.on_hand - self.reserved - self.damaged - self.blocked,
        )
