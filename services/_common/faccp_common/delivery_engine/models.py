"""
Delivery Platform Models & Core Entities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import ClassVar
from .state_machine import DeliveryStatus, VerificationState


@dataclass
class Location:
    latitude: float
    longitude: float
    address_line: str = ""
    city: str = ""
    postal_code: str = ""


@dataclass
class ProofOfDelivery:
    pod_id: str
    delivery_id: str
    status: str = "COMPLETED"
    verification_method: str = "CONTROLLED_HANDOFF"
    completed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class DriverAssignment:
    driver_id: str
    assigned_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "ASSIGNED"


@dataclass
class FulfilmentPlan:
    plan_id: str
    store_id: str
    estimated_duration_minutes: int = 25


@dataclass
class DeliveryJob:
    job_id: str
    order_id: str
    store_id: str
    customer_id: str


@dataclass
class Delivery:
    id: str
    order_id: str
    retailer_id: str
    store_id: str
    customer_id: str
    status: DeliveryStatus
    pickup_location: Location
    dropoff_location: Location
    assigned_driver_id: str | None = None
    verification_state: VerificationState = VerificationState.REQUIRED

    CORE_MODULES: ClassVar[list[str]] = [
        "order-adapter",
        "fulfilment",
        "delivery-orchestrator",
        "dispatch",
        "driver",
        "fleet",
        "routing",
        "tracking",
        "eta",
        "verification",
        "handoff",
        "delivery-zone",
        "serviceability",
        "notifications",
        "cancellation",
        "returns",
        "proof-of-delivery",
        "incident",
        "pricing",
        "analytics",
    ]
