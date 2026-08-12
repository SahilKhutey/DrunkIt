"""Delivery service database models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin, utc_now

from app.db.base import Base


class DeliveryMission(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Delivery Mission orchestrating order fulfillment dispatch."""

    __tablename__ = "delivery_missions"

    mission_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    order_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    store_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    consumer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    status: Mapped[str] = mapped_column(String(32), default="QUEUED", nullable=False, index=True)  # QUEUED | ASSIGNED | PICKED_UP | IN_TRANSIT | COMPLETED | FAILED
    delivery_otp_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    pickup_address: Mapped[str] = mapped_column(String(255), nullable=False)
    dropoff_address: Mapped[str] = mapped_column(String(255), nullable=False)

    assigned_driver_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)

    pings: Mapped[list["DeliveryLocationPing"]] = relationship("DeliveryLocationPing", back_populates="mission", cascade="all, delete-orphan")


class DeliveryAssignment(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Driver assignment record for a delivery mission."""

    __tablename__ = "delivery_assignments"

    mission_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("delivery_missions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    driver_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), default="ACCEPTED", nullable=False)  # ACCEPTED | REJECTED | COMPLETED


class DeliveryLocationPing(UUIDPrimaryKeyMixin, Base):
    """Real-time GPS tracking ping from driver mobile app."""

    __tablename__ = "delivery_location_pings"

    mission_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("delivery_missions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    driver_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    mission: Mapped["DeliveryMission"] = relationship("DeliveryMission", back_populates="pings")


class ProofOfDelivery(UUIDPrimaryKeyMixin, Base):
    """Proof of Delivery (POD) record upon OTP verification at doorstep."""

    __tablename__ = "proof_of_deliveries"

    mission_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("delivery_missions.id", ondelete="CASCADE"), unique=True, nullable=False, index=True
    )
    recipient_verified: Mapped[bool] = mapped_column(Boolean, nullable=False)
    verification_method: Mapped[str] = mapped_column(String(32), default="OTP_SMS", nullable=False)
    verified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
