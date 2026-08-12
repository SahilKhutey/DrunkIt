"""Recommendation service database models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import Float, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from faccp_common.models import TimestampMixin, UUIDPrimaryKeyMixin, utc_now

from app.db.base import Base


class ConsumerPreferenceProfile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Consumer preference profile aggregated from search & purchase history."""

    __tablename__ = "consumer_preference_profiles"

    consumer_id: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, index=True)
    preferred_categories_json: Mapped[str] = mapped_column(Text, nullable=False)
    preferred_brands_json: Mapped[str] = mapped_column(Text, nullable=False)
    price_sensitivity_score: Mapped[float] = mapped_column(Float, default=0.5, nullable=False)


class ProductAffinityScore(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Product co-occurrence / affinity score matrix."""

    __tablename__ = "product_affinity_scores"

    sku_id_a: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    sku_id_b: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    affinity_score: Mapped[float] = mapped_column(Float, nullable=False)
