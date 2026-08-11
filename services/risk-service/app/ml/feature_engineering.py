"""
Feature engineering for risk ML models.
Extracts numeric and categorical features from raw context for consumption by ML models.
"""

from __future__ import annotations

import hashlib
import math
from collections import Counter
from datetime import datetime, timezone
from typing import Any
import numpy as np


class FeatureExtractor:
    """Converts raw context into ML-ready features."""

    FEATURE_NAMES = [
        # Account features
        "account_age_days",
        "failed_verifications",
        "total_orders",
        "successful_deliveries",
        "trust_score",
        "is_flagged",
        # Behavioral features
        "orders_last_1h",
        "orders_last_24h",
        "orders_last_7d",
        "distinct_stores_7d",
        "avg_order_value",
        "max_order_value",
        "order_value_stddev",
        "cart_changes_per_session",
        "address_changes_30d",
        "payment_method_changes_30d",
        "device_changes_30d",
        # Device & network
        "device_user_count",
        "device_orders_30d",
        "distinct_ips_30d",
        "vpn_detected",
        "tor_detected",
        "geo_distance_from_home",
        "geo_country_mismatch",
        "user_agent_changes_30d",
        "device_trust_score",
        # Temporal
        "order_hour",
        "order_day_of_week",
        "is_late_night",
        "is_weekend",
        "seconds_since_last_order",
        "seconds_since_last_login",
        # Payment
        "payment_failures_30d",
        "card_bin_changes_30d",
        "velocity_amount_1h",
        "velocity_amount_24h",
        # Identity
        "identity_verified",
        "age_eligible",
        "address_verified",
        "identity_age_days",
        # Compliance
        "compliance_violations_30d",
        "age_verification_age_days",
        # Aggregations
        "lifetime_value",
        "average_delivery_rating",
        "cancellation_rate",
    ]

    def extract(
        self, context: dict[str, Any], history: list[dict[str, Any]] | None = None
    ) -> np.ndarray:
        """Extract features as a numpy array."""
        now = datetime.now(timezone.utc)
        history = history or []

        # Account
        account_age_days = context.get("account_age_days", 0)
        failed_verifications = context.get("failed_verifications", 0)
        total_orders = context.get("total_orders", 0)
        successful_deliveries = context.get("successful_deliveries", 0)
        trust_score = context.get("trust_score", 50)
        is_flagged = int(context.get("is_flagged", False))

        # Behavioral
        orders_1h = sum(1 for h in history if h.get("minutes_ago", 99999) < 60)
        orders_24h = sum(1 for h in history if h.get("minutes_ago", 99999) < 1440)
        orders_7d = sum(1 for h in history if h.get("minutes_ago", 99999) < 10080)
        distinct_stores_7d = len(set(h.get("store_id") for h in history if h.get("minutes_ago", 99999) < 10080))
        order_values = [h.get("amount", 0) for h in history if h.get("amount")]
        avg_order_value = float(np.mean(order_values)) if order_values else 0.0
        max_order_value = float(np.max(order_values)) if order_values else 0.0
        order_value_stddev = float(np.std(order_values)) if len(order_values) > 1 else 0.0

        cart_changes = context.get("cart_changes_per_session", 0)
        address_changes_30d = context.get("address_changes_30d", 0)
        payment_method_changes_30d = context.get("payment_method_changes_30d", 0)
        device_changes_30d = context.get("device_changes_30d", 0)

        # Device
        device_user_count = context.get("device_user_count", 1)
        device_orders_30d = context.get("device_orders_30d", 0)
        distinct_ips_30d = context.get("distinct_ips_30d", 1)
        vpn_detected = int(context.get("vpn_detected", False))
        tor_detected = int(context.get("tor_detected", False))
        geo_distance_from_home = context.get("geo_distance_from_home_km", 0)
        geo_country_mismatch = int(context.get("geo_country_mismatch", False))
        ua_changes_30d = context.get("user_agent_changes_30d", 0)
        device_trust_score = context.get("device_trust_score", 50)

        # Temporal
        order_hour = context.get("order_hour", now.hour)
        order_dow = context.get("order_day_of_week", now.weekday())
        is_late_night = int(order_hour < 6 or order_hour > 22)
        is_weekend = int(order_dow >= 5)
        seconds_since_last_order = context.get("seconds_since_last_order", 999999)
        seconds_since_last_login = context.get("seconds_since_last_login", 0)

        # Payment
        payment_failures_30d = context.get("payment_failures_30d", 0)
        card_bin_changes_30d = context.get("card_bin_changes_30d", 0)
        velocity_amount_1h = sum(h.get("amount", 0) for h in history if h.get("minutes_ago", 99999) < 60)
        velocity_amount_24h = sum(h.get("amount", 0) for h in history if h.get("minutes_ago", 99999) < 1440)

        # Identity
        identity_verified = int(context.get("identity_verified", False))
        age_eligible = int(context.get("age_eligible", False))
        address_verified = int(context.get("address_verified", False))
        identity_age_days = context.get("identity_age_days", 0)

        # Compliance
        compliance_violations_30d = context.get("compliance_violations_30d", 0)
        age_verification_age_days = context.get("age_verification_age_days", 0)

        # Aggregations
        lifetime_value = sum(order_values)
        avg_rating = context.get("avg_delivery_rating", 5.0)
        cancellation_rate = context.get("cancellation_rate", 0.0)

        features = np.array([
            account_age_days, failed_verifications, total_orders, successful_deliveries, trust_score, is_flagged,
            orders_1h, orders_24h, orders_7d, distinct_stores_7d, avg_order_value, max_order_value, order_value_stddev,
            cart_changes, address_changes_30d, payment_method_changes_30d, device_changes_30d,
            device_user_count, device_orders_30d, distinct_ips_30d, vpn_detected, tor_detected, geo_distance_from_home, geo_country_mismatch, ua_changes_30d, device_trust_score,
            order_hour, order_dow, is_late_night, is_weekend, seconds_since_last_order, seconds_since_last_login,
            payment_failures_30d, card_bin_changes_30d, velocity_amount_1h, velocity_amount_24h,
            identity_verified, age_eligible, address_verified, identity_age_days,
            compliance_violations_30d, age_verification_age_days,
            lifetime_value, avg_rating, cancellation_rate,
        ], dtype=np.float32)

        # Replace NaN/Inf
        features = np.nan_to_num(features, nan=0.0, posinf=1e6, neginf=-1e6)
        return features

    def feature_vector_to_dict(self, features: np.ndarray) -> dict[str, float]:
        """Convert feature array back to a labeled dict (for explainability)."""
        return {name: float(features[i]) for i, name in enumerate(self.FEATURE_NAMES) if i < len(features)}
