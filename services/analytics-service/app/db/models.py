"""Analytics service database models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin, utc_now

from app.db.base import Base


class MetricAggregate(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Pre-computed time-series metric aggregate."""

    __tablename__ = "metric_aggregates"

    metric_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    dimension_key: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # e.g., STORE_ID or STATE_CODE
    dimension_value: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    metric_value: Mapped[float] = mapped_column(Float, nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ReportSnapshot(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Historical snapshot report generated for compliance auditors."""

    __tablename__ = "report_snapshots"

    snapshot_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    report_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # EXCISE_TAX | COMPLIANCE_SUMMARY
    generated_by: Mapped[str] = mapped_column(String(64), nullable=False)
    snapshot_data_json: Mapped[str] = mapped_column(Text, nullable=False)
