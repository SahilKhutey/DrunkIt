"""
Portal Definitions & Visual Principles.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import ClassVar


class PortalType(str, Enum):
    CONSUMER = "CONSUMER"
    RETAILER = "RETAILER"
    ADMIN = "ADMIN"
    DEVELOPER = "DEVELOPER"


@dataclass
class PortalDefinition:
    type: PortalType
    name: str
    target_audience: str
    visual_weight: str
    information_density: str
    path: str


class PortalRegistry:
    PORTALS: ClassVar[dict[PortalType, PortalDefinition]] = {
        PortalType.CONSUMER: PortalDefinition(
            type=PortalType.CONSUMER,
            name="Consumer Portal",
            target_audience="End Users / Consumers",
            visual_weight="Light, spacious, calm",
            information_density="Low to Medium",
            path="apps/consumer-web/",
        ),
        PortalType.RETAILER: PortalDefinition(
            type=PortalType.RETAILER,
            name="Retailer Portal",
            target_audience="Retailer Staff & Managers",
            visual_weight="Operational, functional, fast",
            information_density="High",
            path="apps/retailer-web/",
        ),
        PortalType.ADMIN: PortalDefinition(
            type=PortalType.ADMIN,
            name="Admin Portal",
            target_audience="Platform Admins & Regulators",
            visual_weight="Information-dense, systematic",
            information_density="Very High",
            path="apps/admin-web/",
        ),
        PortalType.DEVELOPER: PortalDefinition(
            type=PortalType.DEVELOPER,
            name="Developer Portal",
            target_audience="Developers & Integrators",
            visual_weight="Code-first, technical",
            information_density="Medium (technical)",
            path="apps/developer-web/",
        ),
    }

    PRINCIPLES: ClassVar[list[str]] = [
        "P1 — Role Separation",
        "P2 — Progressive Disclosure",
        "P3 — Action Clarity",
        "P4 — Safety First",
        "P5 — Trust Visibility",
        "P6 — Consistency",
    ]

    STATUS_TREATMENTS: ClassVar[dict[str, str]] = {
        "Verified": "Checkmark + Green",
        "Pending": "Clock + Yellow",
        "Requires Action": "Alert + Orange",
        "Restricted": "Lock + Red",
        "Unavailable": "Dash + Gray",
        "Suspended": "Pause + Red",
        "Expired": "X + Gray",
    }
