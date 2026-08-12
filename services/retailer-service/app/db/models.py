"""Retailer service database models."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Index, Integer, String, Text, Time
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin, utc_now

from app.db.base import Base


class RetailerOrganization(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Legal business entity operating stores."""

    __tablename__ = "retailer_organizations"

    legal_name: Mapped[str] = mapped_column(String(128), nullable=False)
    trade_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    business_type: Mapped[str] = mapped_column(String(64), nullable=False)  # PROPRIETORSHIP | PARTNERSHIP | PRIVATE_LIMITED | PUBLIC_LIMITED
    gstin: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    pan: Mapped[str] = mapped_column(String(16), unique=True, nullable=False, index=True)

    owner_user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    seller_level: Mapped[str] = mapped_column(String(32), default="S1_BASIC", nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    stores: Mapped[list["Store"]] = relationship(
        "Store", back_populates="organization", cascade="all, delete-orphan"
    )


class Store(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Physical licensed store location."""

    __tablename__ = "stores"

    organization_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("retailer_organizations.id", ondelete="CASCADE"), nullable=False, index=True
    )

    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    store_type: Mapped[str] = mapped_column(String(32), default="CL_2", nullable=False)  # CL_2 | CL_9 | MSIL | RETREAT

    address_line_1: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line_2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    pincode: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    jurisdiction: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_accepting_orders: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    organization: Mapped["RetailerOrganization"] = relationship("RetailerOrganization", back_populates="stores")
    licenses: Mapped[list["StoreLicense"]] = relationship(
        "StoreLicense", back_populates="store", cascade="all, delete-orphan"
    )
    operating_hours: Mapped[list["StoreOperatingHours"]] = relationship(
        "StoreOperatingHours", back_populates="store", cascade="all, delete-orphan"
    )


class StoreLicense(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """State Excise License for a store location."""

    __tablename__ = "store_licenses"

    store_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True
    )

    license_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    license_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # CL_2 | CL_9 | FL_3 | EXP
    issuing_authority: Mapped[str] = mapped_column(String(128), nullable=False)
    jurisdiction: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_until: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    status: Mapped[str] = mapped_column(String(32), default="ACTIVE", nullable=False, index=True)  # ACTIVE | EXPIRED | SUSPENDED | REVOKED
    document_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    store: Mapped["Store"] = relationship("Store", back_populates="licenses")


class StoreOperatingHours(UUIDPrimaryKeyMixin, Base):
    """Permitted store operational hours per day of week."""

    __tablename__ = "store_operating_hours"

    store_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True
    )

    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Monday .. 6=Sunday
    open_time: Mapped[time] = mapped_column(Time, nullable=False)
    close_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    store: Mapped["Store"] = relationship("Store", back_populates="operating_hours")


class StoreStaffAssignment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Staff member assigned to a store location."""

    __tablename__ = "store_staff_assignments"

    store_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    role_in_store: Mapped[str] = mapped_column(String(32), nullable=False)  # STORE_MANAGER | STORE_OPERATOR | PACKER | INVENTORY_MANAGER
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
