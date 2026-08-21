"""Retailer domain models for merchants, locations, jurisdictions, and excise licences."""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class Retailer(Base):
    """Licensed retailer commercial entity."""

    __tablename__ = "retailers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    licence_status: Mapped[str] = mapped_column(String(50), nullable=False, default="UNKNOWN")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    locations: Mapped[list["RetailerLocation"]] = relationship(
        "RetailerLocation",
        back_populates="retailer",
        cascade="all, delete-orphan",
    )
    licences: Mapped[list["RetailerLicence"]] = relationship(
        "RetailerLicence",
        back_populates="retailer",
        cascade="all, delete-orphan",
    )


class RetailerLocation(Base):
    """Physical licensed retail store outlet."""

    __tablename__ = "retailer_locations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    retailer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("retailers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state_code: Mapped[str] = mapped_column(String(10), nullable=False)
    postal_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    country_code: Mapped[str] = mapped_column(String(2), nullable=False, default="IN")
    latitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE")

    __table_args__ = (
        Index("idx_retailer_locations_geo", "country_code", "state_code", "city"),
    )

    # Relationships
    retailer: Mapped["Retailer"] = relationship("Retailer", back_populates="locations")


class Jurisdiction(Base):
    """Sovereign or state/provincial regulatory jurisdiction."""

    __tablename__ = "jurisdictions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    country_code: Mapped[str] = mapped_column(String(2), nullable=False)
    state_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    timezone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE")

    __table_args__ = (
        UniqueConstraint("country_code", "state_code", name="uq_jurisdiction_country_state"),
    )

    # Relationships
    licences: Mapped[list["RetailerLicence"]] = relationship(
        "RetailerLicence",
        back_populates="jurisdiction",
    )


class RetailerLicence(Base):
    """Excise retail operating licence."""

    __tablename__ = "retailer_licences"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    retailer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("retailers.id", ondelete="CASCADE"),
        nullable=False,
    )
    jurisdiction_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jurisdictions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    licence_number: Mapped[str] = mapped_column(String(100), nullable=False)
    licence_type: Mapped[str] = mapped_column(String(50), nullable=False)
    valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="PENDING")
    evidence_uri: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    retailer: Mapped["Retailer"] = relationship("Retailer", back_populates="licences")
    jurisdiction: Mapped["Jurisdiction"] = relationship("Jurisdiction", back_populates="licences")
