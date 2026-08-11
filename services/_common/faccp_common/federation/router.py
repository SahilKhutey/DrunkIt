"""
Jurisdiction-based request router.
Routes requests to the correct regional/state service cluster based on consumer's address, store location, or order jurisdiction.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Region(str, Enum):
    INDIA_NORTH = "IN-N"
    INDIA_SOUTH = "IN-S"
    INDIA_EAST = "IN-E"
    INDIA_WEST = "IN-W"
    INDIA_CENTRAL = "IN-C"
    INTERNATIONAL = "INTL"


@dataclass
class JurisdictionConfig:
    code: str
    name: str
    region: Region
    service_cluster: str
    compliance_policy_version: str = "1.0"
    enabled: bool = True
    is_primary: bool = False
    fallback_to: str | None = None
    allowed_origins: list[str] = field(default_factory=list)
    data_residency_required: bool = True


JURISDICTION_REGISTRY: dict[str, JurisdictionConfig] = {
    "IN-CG": JurisdictionConfig(
        code="IN-CG", name="Chhattisgarh", region=Region.INDIA_CENTRAL, service_cluster="faccp-cg-prod", is_primary=True,
    ),
    "IN-MH": JurisdictionConfig(
        code="IN-MH", name="Maharashtra", region=Region.INDIA_WEST, service_cluster="faccp-mh-prod",
    ),
    "IN-KA": JurisdictionConfig(
        code="IN-KA", name="Karnataka", region=Region.INDIA_SOUTH, service_cluster="faccp-ka-prod",
    ),
    "IN-DL": JurisdictionConfig(
        code="IN-DL", name="Delhi", region=Region.INDIA_NORTH, service_cluster="faccp-dl-prod",
    ),
    "IN-TN": JurisdictionConfig(
        code="IN-TN", name="Tamil Nadu", region=Region.INDIA_SOUTH, service_cluster="faccp-tn-prod",
    ),
    "IN-GA": JurisdictionConfig(
        code="IN-GA", name="Goa", region=Region.INDIA_WEST, service_cluster="faccp-ga-prod",
    ),
}


@dataclass
class FederatedRequest:
    request_id: str
    jurisdiction_code: str | None
    consumer_id: str | None
    payload: dict[str, Any]
    headers: dict[str, str] = field(default_factory=dict)
    actor_id: str | None = None
    actor_role: str | None = None
    target_service: str | None = None


class JurisdictionRouter:

    def __init__(self, registry: dict[str, JurisdictionConfig] | None = None) -> None:
        self.registry = registry or JURISDICTION_REGISTRY

    def resolve_cluster(self, jurisdiction_code: str) -> JurisdictionConfig | None:
        return self.registry.get(jurisdiction_code.upper())

    def get_service_endpoint(self, jurisdiction_code: str, service_name: str) -> str | None:
        config = self.resolve_cluster(jurisdiction_code)
        if not config or not config.enabled:
            return None
        return f"{service_name}.{config.service_cluster}.svc.cluster.local"

    def route(self, request: FederatedRequest) -> dict[str, Any] | None:
        if not request.jurisdiction_code:
            return {"action": "reject", "reason": "jurisdiction_required"}
        config = self.resolve_cluster(request.jurisdiction_code)
        if not config:
            return {"action": "reject", "reason": "unknown_jurisdiction"}
        if not config.enabled:
            return {"action": "reject", "reason": "jurisdiction_disabled"}

        if config.data_residency_required and request.payload:
            consumer_region = request.payload.get("consumer_region")
            if consumer_region and consumer_region != config.region.value:
                return {
                    "action": "reject",
                    "reason": "data_residency_violation",
                    "jurisdiction": config.code,
                    "expected_region": config.region.value,
                    "actual_region": consumer_region,
                }

        return {
            "action": "route",
            "jurisdiction": config.code,
            "region": config.region.value,
            "cluster": config.service_cluster,
            "compliance_version": config.compliance_policy_version,
        }

    def is_jurisdiction_allowed(self, jurisdiction_code: str, user_jurisdictions: list[str]) -> bool:
        return jurisdiction_code.upper() in [j.upper() for j in user_jurisdictions]
