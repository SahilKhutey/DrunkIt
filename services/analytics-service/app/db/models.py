"""
Analytics models — archived events, hourly/daily aggregates, dashboard snapshots.
"""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Any
from sqlalchemy import Boolean, DateTime, Date, Index, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from faccp_common.models import UUIDPrimaryKeyMixin
from app.db.base import Base


class EventArchive(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "event_archive"

    event_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    producer: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    tenant_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    archived_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)


class DailyStoreMetric(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "daily_store_metrics"

    store_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    retailer_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    metric_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    total_orders: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    gross_revenue: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    net_revenue: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    avg_order_value: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    cancelled_orders: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    compliance_denials: Mapped[int] = mapped_column(Integer, default=0, nullable=False)


class DailyPlatformMetric(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "daily_platform_metrics"

    metric_date: Mapped[date] = mapped_column(Date, unique=True, nullable=False, index=True)
    total_orders: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    gross_volume: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=0, nullable=False)
    platform_revenue: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0, nullable=False)
    active_consumers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    active_stores: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    compliance_checks_run: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    compliance_denial_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0, nullable=False)
