"""Compliance reporting service — database models."""

from __future__ import annotations
from datetime import datetime
from typing import Any
from sqlalchemy import Boolean, DateTime, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin
from app.db.base import Base


class ComplianceReport(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "compliance_reports"

    report_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    report_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    jurisdiction_code: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    generated_by: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="ready", nullable=False)


class ReportSchedule(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "report_schedules"

    report_type: Mapped[str] = mapped_column(String(64), nullable=False)
    jurisdiction_code: Mapped[str] = mapped_column(String(32), nullable=False)
    schedule_cron: Mapped[str] = mapped_column(String(64), nullable=False)
    recipients: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by: Mapped[str] = mapped_column(String(128), nullable=False)
