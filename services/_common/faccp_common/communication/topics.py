"""Central topic registry for all Kafka topics."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TopicSpec:
    name: str
    partitions: int = 3
    retention_ms: int = 7_776_000_000  # 90 days
    description: str = ""


class TopicRegistry:
    """Central definition of all event topics."""

    # Identity
    IDENTITY_EVENTS = TopicSpec("identity.events", description="User lifecycle events")
    VERIFICATION_EVENTS = TopicSpec("verification.events", description="KYC/age/license events")

    # Consumer
    CONSUMER_EVENTS = TopicSpec("consumer.events", description="Consumer profile events")

    # Retailer
    RETAILER_EVENTS = TopicSpec("retailer.events", description="Retailer/org/store/staff events")

    # Catalog
    CATALOG_EVENTS = TopicSpec("catalog.events", description="Product/SKU/brand events")
    INVENTORY_EVENTS = TopicSpec("inventory.events", description="Stock events")

    # Commerce
    ORDER_EVENTS = TopicSpec("order.events", partitions=6, description="Order lifecycle events")
    PAYMENT_EVENTS = TopicSpec("payment.events", description="Payment/transaction events")

    # Delivery
    DELIVERY_EVENTS = TopicSpec("delivery.events", description="Delivery lifecycle events")

    # Compliance
    COMPLIANCE_EVENTS = TopicSpec("compliance.events", description="Policy/decision events")

    # Trust
    RISK_EVENTS = TopicSpec("risk.events", description="Risk evaluation events")

    # Audit
    AUDIT_EVENTS = TopicSpec("audit.events", description="Immutable audit events")

    # Pricing
    PRICING_EVENTS = TopicSpec("pricing.events", description="Price/calculation events")

    # Notifications (internal)
    NOTIFICATION_EVENTS = TopicSpec("notification.events", description="Outbound notifications")

    # Listing
    LISTING_EVENTS = TopicSpec("listing.events", description="Listing lifecycle events")

    @classmethod
    def all_topics(cls) -> list[TopicSpec]:
        return [
            v for k, v in vars(cls).items()
            if isinstance(v, TopicSpec)
        ]

    @classmethod
    def all_names(cls) -> list[str]:
        return [t.name for t in cls.all_topics()]
