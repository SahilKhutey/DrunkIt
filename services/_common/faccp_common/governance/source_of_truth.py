"""
Source of Truth Protocol implementation (§13.1, §13.4, §13.11).
Central registry for data ownership, conflict resolution, and cross-domain data sharing policies.
"""

from __future__ import annotations

import logging
from typing import Any, ClassVar

logger = logging.getLogger(__name__)


class SourceOfTruthRegistry:
    """Central registry of information domain ownership across FACCP platform."""

    OWNERSHIP: ClassVar[dict[str, tuple[str, str]]] = {
        # Identity
        "user_account": ("identity-service", "users table"),
        "session": ("identity-service", "sessions table"),
        "api_key": ("identity-service", "api_keys table"),
        "role": ("identity-service", "role_definitions table"),
        "device": ("identity-service", "devices table"),
        "mfa_enrollment": ("identity-service", "users.mfa_* columns"),

        # Consumer
        "consumer_profile": ("consumer-service", "consumers table"),
        "consumer_pii": ("consumer-service", "consumers.first_name_encrypted, etc."),
        "consumer_address": ("consumer-service", "consumer_addresses table"),
        "consumer_consent": ("consumer-service", "consents table"),
        "consumer_verification": ("consumer-service", "verification_records table"),

        # Retailer
        "organization": ("retailer-service", "organizations table"),
        "retailer_license": ("retailer-service", "licenses table"),
        "store": ("retailer-service", "stores table"),
        "retailer_staff": ("retailer-service", "staff table"),

        # Catalog & Inventory
        "product": ("catalog-service", "products table"),
        "category": ("catalog-service", "categories table"),
        "brand": ("catalog-service", "brands table"),
        "inventory_level": ("inventory-service", "inventory table"),
        "inventory_reservation": ("inventory-service", "inventory_reservations table"),
        "stock_movement": ("inventory-service", "stock_movements table"),

        # Commerce
        "order": ("order-service", "orders table"),
        "order_item": ("order-service", "order_items table"),
        "order_state_history": ("order-service", "order_state_history table"),
        "cart": ("order-service", "carts table"),
        "price_calculation": ("pricing-service", "price_calculations table"),
        "price_book": ("pricing-service", "price_books table"),
        "promotion": ("pricing-service", "promotions table"),
        "tax_rule": ("pricing-service", "tax_rules table"),

        # Compliance
        "jurisdiction": ("compliance-service", "jurisdictions table"),
        "compliance_policy": ("compliance-service", "policies table"),
        "dry_day": ("compliance-service", "dry_days table"),
        "product_classification": ("compliance-service", "product_classifications table"),
        "compliance_decision": ("compliance-service", "decisions table"),
        "policy_migration": ("compliance-service", "policy_migrations table"),

        # Audit & Risk
        "audit_event": ("audit-service", "audit_events table"),
        "risk_profile": ("risk-service", "risk_profiles table"),
        "fraud_case": ("risk-service", "fraud_cases table"),

        # Delivery & Payment
        "driver": ("delivery-service", "drivers table"),
        "delivery": ("delivery-service", "deliveries table"),
        "payment_intent": ("payment-service", "payment_intents table"),
        "payment_transaction": ("payment-service", "payment_transactions table"),
        "refund": ("payment-service", "refunds table"),
        "ledger_entry": ("payment-service", "ledger_entries table"),

        # Notification & Whitelabel
        "notification_template": ("notification-service", "notification_templates table"),
        "tenant": ("whitelabel-service", "tenants table"),
    }

    @classmethod
    def get_owner(cls, information: str) -> tuple[str, str]:
        """Return (service, table) that owns a piece of information."""
        if information not in cls.OWNERSHIP:
            raise ValueError(
                f"No source of truth defined for '{information}'. "
                f"Add it to SourceOfTruthRegistry.OWNERSHIP"
            )
        return cls.OWNERSHIP[information]


class SourceOfTruthResolver:
    """Ensures source of truth always wins when projections differ from source."""

    @staticmethod
    def resolve_conflict(projection_value: Any, source_value: Any, field_name: str) -> Any:
        """When projection and source differ, return source value and log warning."""
        if projection_value != source_value:
            logger.warning(
                "source_of_truth_conflict field=%s projection=%s source=%s resolution=source_wins",
                field_name,
                projection_value,
                source_value,
            )
        return source_value


class DataSharingPolicy:
    """Defines allowed minimum fields when data crosses domain boundaries."""

    CONSUMER_FOR_ORDER: ClassVar[frozenset[str]] = frozenset({
        "consumer_id", "consumer_level", "age_eligible", "is_active", "email_verified"
    })

    PRODUCT_FOR_ORDER: ClassVar[frozenset[str]] = frozenset({
        "product_id", "sku", "name", "category", "abv", "volume_ml", "base_price", "is_active"
    })

    ORDER_FOR_CONSUMER: ClassVar[frozenset[str]] = frozenset({
        "order_id", "order_number", "state", "items", "total_amount", "placed_at", "delivered_at"
    })

    @classmethod
    def filter_for_recipient(cls, data: dict[str, Any], recipient: str, entity_type: str) -> dict[str, Any]:
        """Filters input dictionary to include only fields allowed for the recipient."""
        attr_name = f"{entity_type.upper()}_FOR_{recipient.upper()}"
        allowed_fields = getattr(cls, attr_name, None)
        if allowed_fields is None:
            return data
        return {k: v for k, v in data.items() if k in allowed_fields}
