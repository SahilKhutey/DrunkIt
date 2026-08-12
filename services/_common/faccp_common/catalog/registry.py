"""
Catalog Registry & Lifecycle Management.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, ClassVar


class CatalogLayer(str, Enum):
    ADMINISTRATIVE = "ADMINISTRATIVE"
    DEVELOPER = "DEVELOPER"
    TEMPLATE = "TEMPLATE"
    REGISTRY = "REGISTRY"


class CatalogLifecycleState(str, Enum):
    DRAFT = "DRAFT"
    VALIDATING = "VALIDATING"
    REVIEW = "REVIEW"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"


@dataclass
class CatalogObject:
    object_id: str
    name: str
    layer: CatalogLayer
    sub_catalog: str
    version: str = "1.0.0"
    owner: str = "platform-team"
    state: CatalogLifecycleState = CatalogLifecycleState.DRAFT
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class CatalogRegistry:
    ADMIN_SUB_CATALOGS: ClassVar[list[str]] = [
        "ADM-CAT-01 Organization Catalog",
        "ADM-CAT-02 Jurisdiction Catalog",
        "ADM-CAT-03 Policy Catalog",
        "ADM-CAT-04 Role Catalog",
        "ADM-CAT-05 Permission Catalog",
        "ADM-CAT-06 Workflow Catalog",
        "ADM-CAT-07 Compliance Rule Catalog",
        "ADM-CAT-08 Product Classification Catalog",
        "ADM-CAT-09 Retailer Catalog",
        "ADM-CAT-10 Store Catalog",
    ]

    DEVELOPER_SUB_CATALOGS: ClassVar[list[str]] = [
        "DEV-CAT-01 Service Catalog",
        "DEV-CAT-02 API Catalog",
        "DEV-CAT-03 Event Catalog",
        "DEV-CAT-04 Schema Catalog",
        "DEV-CAT-05 Service Dependency Catalog",
        "DEV-CAT-06 Integration Catalog",
        "DEV-CAT-07 SDK Catalog",
        "DEV-CAT-08 Component Catalog",
    ]

    def __init__(self) -> None:
        self.objects: dict[str, CatalogObject] = {}

    def register(self, obj: CatalogObject) -> None:
        self.objects[obj.object_id] = obj

    def transition_state(self, object_id: str, new_state: CatalogLifecycleState) -> None:
        if object_id not in self.objects:
            raise KeyError(f"Catalog object '{object_id}' not found")
        self.objects[object_id].state = new_state
