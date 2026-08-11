"""
Policy replication service.
Replicates policy updates from a primary jurisdiction to secondary jurisdictions.
"""

from __future__ import annotations

import asyncio
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import httpx

from faccp_common.events import make_event
from faccp_common.kafka_client import EventProducer
from faccp_common.logging import get_logger

logger = get_logger(__name__)


@dataclass
class PolicyVersion:
    policy_id: str
    version: str
    jurisdiction_code: str
    rules: dict[str, Any]
    checksum: str
    effective_from: datetime
    source: str  # "primary" | "replicated"
    replicated_from: str | None = None


class PolicyReplicator:

    def __init__(self, http_client: httpx.AsyncClient, producer: EventProducer | None = None) -> None:
        self._http = http_client
        self.producer = producer
        self.replication_log: list[dict[str, Any]] = []

    async def replicate_policy(
        self, policy: PolicyVersion, target_jurisdictions: list[str], source_endpoint: str
    ) -> dict[str, Any]:
        results = {"succeeded": [], "failed": []}
        for target in target_jurisdictions:
            try:
                response = await self._http.post(
                    f"{source_endpoint}/api/v1/policies",
                    json={
                        "jurisdiction_code": target,
                        "policy_type": self._infer_type(policy),
                        "version": policy.version,
                        "name": f"Replicated from {policy.jurisdiction_code} v{policy.version}",
                        "rules": policy.rules,
                        "effective_from": policy.effective_from.isoformat(),
                        "approved_by": f"replicator:{policy.jurisdiction_code}",
                        "source_document": f"Replicated from {policy.policy_id}",
                    },
                    timeout=15.0,
                )
                if response.status_code in (200, 201):
                    results["succeeded"].append(target)
                else:
                    results["failed"].append({"target": target, "error": response.text})
            except Exception as e:
                logger.exception("policy_replication_failed", target=target)
                results["failed"].append({"target": target, "error": str(e)})

        replication_record = {
            "policy_id": policy.policy_id,
            "version": policy.version,
            "source_jurisdiction": policy.jurisdiction_code,
            "targets": target_jurisdictions,
            "results": results,
            "replicated_at": datetime.now(timezone.utc).isoformat(),
        }
        self.replication_log.append(replication_record)

        if self.producer:
            try:
                await self.producer.publish("policy.events", make_event(
                    "policy.replicated", replication_record, producer="faccp-policy-replicator"
                ))
            except Exception:
                pass

        return results

    async def verify_replication(
        self, policy_id: str, jurisdictions: list[str], source_endpoint: str
    ) -> dict[str, Any]:
        discrepancies = []
        for j in jurisdictions:
            try:
                response = await self._http.get(
                    f"{source_endpoint}/api/v1/policies/{j}/license",
                    timeout=10.0,
                )
                if response.status_code != 200:
                    discrepancies.append({"jurisdiction": j, "issue": "policy_not_found"})
            except Exception as e:
                discrepancies.append({"jurisdiction": j, "issue": "fetch_error", "error": str(e)})

        return {
            "policy_id": policy_id,
            "checked_jurisdictions": len(jurisdictions),
            "discrepancies": discrepancies,
            "is_consistent": len(discrepancies) == 0,
        }

    def _infer_type(self, policy: PolicyVersion) -> str:
        if "min_age" in policy.rules: return "age"
        if "start" in policy.rules and "end" in policy.rules: return "hours"
        if "allowed_categories" in policy.rules: return "product"
        if "permitted_zones" in policy.rules: return "delivery"
        return "sale"
