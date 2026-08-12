"""
Data Minimization Policy as codified in Article 2 of the System Constitution (§2.1).
"""

from __future__ import annotations
from typing import Any


class DataMinimizationPolicy:
    CONSUMER_PROFILE_REQUIRED: frozenset[str] = frozenset({
        "consumer_id",
        "consumer_level",
        "age_eligible",
        "display_name",
        "is_active",
        "email_verified",
    })

    CONSUMER_PROFILE_PII: frozenset[str] = frozenset({
        "first_name",
        "last_name",
        "date_of_birth",
        "email",
        "phone",
        "address_line1",
        "address_line2",
    })

    @classmethod
    def filter_for_service(cls, consumer_data: dict[str, Any], target_service: str) -> dict[str, Any]:
        """Return only the fields target_service is explicitly authorized to view."""
        policies: dict[str, frozenset[str]] = {
            "order-service": cls.CONSUMER_PROFILE_REQUIRED,
            "delivery-service": cls.CONSUMER_PROFILE_REQUIRED | {"phone", "delivery_zone"},
            "marketing-service": cls.CONSUMER_PROFILE_REQUIRED | {"email"},
            "analytics-service": {"consumer_id_hash", "consumer_level", "cohort"},
            "identity-service": cls.CONSUMER_PROFILE_REQUIRED | cls.CONSUMER_PROFILE_PII,
        }
        allowed = policies.get(target_service, cls.CONSUMER_PROFILE_REQUIRED)
        return {k: v for k, v in consumer_data.items() if k in allowed}
