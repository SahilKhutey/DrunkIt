"""
Data Retention Policy as codified in Article 2 of the System Constitution (§2.4).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any


class RetentionPolicy:
    POLICIES: dict[str, timedelta] = {
        "consumer_pii": timedelta(days=30),  # post-deletion grace period
        "transaction": timedelta(days=8 * 365),
        "audit_event": timedelta(days=8 * 365),
        "session": timedelta(days=30),
        "consent_record": timedelta(days=7 * 365),
        "gps_tracking": timedelta(days=90),
        "delivery_proof": timedelta(days=8 * 365),
    }

    @classmethod
    def get_cutoff(cls, data_type: str, now: datetime | None = None) -> datetime:
        """Returns the cutoff timestamp older than which data must be deleted."""
        now = now or datetime.now(timezone.utc)
        retention = cls.POLICIES.get(data_type, timedelta(days=30))
        return now - retention
