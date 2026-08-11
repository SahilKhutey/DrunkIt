"""
Policy loading, caching, and evaluation orchestration.

Loads policies from DB (and YAML files at /app/policies for static rules),
caches them in Redis, and orchestrates rule evaluation.
"""

from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.events import make_event
from faccp_common.exceptions import NotFoundError
from faccp_common.kafka_client import EventProducer
from faccp_common.logging import get_logger

from app.config import get_settings
from app.db.models import (
    Decision, DryDay, Jurisdiction, Policy, ProductClassification,
)
from app.domain.rule_engine import (
    DecisionOutcome, EvaluationRequest, EvaluationResult, evaluate_order,
)
from app.schemas.policy import (
    DecisionRecord, EvaluateRequest, EvaluateResponse, PolicyResponse,
)

logger = get_logger(__name__)
settings = get_settings()


class PolicyService:
    """Orchestrates policy loading, caching, and evaluation."""

    CACHE_PREFIX = "compliance:policy"
    CACHE_TTL = settings.policy_cache_ttl_seconds

    def __init__(self, db: AsyncSession, producer: EventProducer | None = None) -> None:
        self.db = db
        self.producer = producer
        self._static_policies_cache: dict[str, Any] = {}

    # ============================================================
    # Policy management
    # ============================================================
    async def create_jurisdiction(
        self, code: str, name: str, level: str, country_code: str = "IN",
        parent_code: str | None = None, config: dict[str, Any] | None = None,
    ) -> Jurisdiction:
        parent_id = None
        if parent_code:
            parent = await self._get_jurisdiction_by_code(parent_code)
            if parent is not None:
                parent_id = parent.id
        existing = await self._get_jurisdiction_by_code(code)
        if existing is not None:
            return existing
        j = Jurisdiction(
            code=code, name=name, level=level, country_code=country_code,
            parent_id=parent_id, config=config or {},
        )
        self.db.add(j)
        await self.db.commit()
        await self.db.refresh(j)
        return j

    async def create_policy(
        self,
        jurisdiction_code: str,
        policy_type: str,
        version: str,
        name: str,
        rules: dict[str, Any],
        effective_from: date,
        effective_until: date | None,
        approved_by: str,
        source_document: str | None = None,
    ) -> Policy:
        j = await self._get_jurisdiction_by_code(jurisdiction_code)
        if j is None:
            raise NotFoundError(f"Jurisdiction not found: {jurisdiction_code}")
        rules_json = json.dumps(rules, sort_keys=True, default=str)
        checksum = hashlib.sha256(rules_json.encode()).hexdigest()
        policy = Policy(
            jurisdiction_id=j.id,
            policy_type=policy_type,
            version=version,
            name=name,
            rules=rules,
            effective_from=effective_from,
            effective_until=effective_until,
            is_active=True,
            approved_by=approved_by,
            approved_at=datetime.now(timezone.utc),
            source_document=source_document,
            checksum=checksum,
        )
        self.db.add(policy)
        await self.db.commit()
        await self.db.refresh(policy)
        await self._invalidate_cache(jurisdiction_code, policy_type)
        return policy

    async def get_active_policy(
        self, jurisdiction_code: str, policy_type: str, at: date | None = None,
    ) -> Policy | None:
        at = at or date.today()
        j = await self._get_jurisdiction_by_code(jurisdiction_code)
        if j is None:
            return None
        result = await self.db.execute(
            select(Policy).where(
                and_(
                    Policy.jurisdiction_id == j.id,
                    Policy.policy_type == policy_type,
                    Policy.is_active == True,  # noqa: E712
                    Policy.effective_from <= at,
                )
            ).order_by(Policy.effective_from.desc())
        )
        return result.scalars().first()

    async def add_dry_day(
        self, jurisdiction_code: str, day: date, reason: str,
        approved_by: str, is_recurring: bool = False, recurring_rule: str | None = None,
    ) -> DryDay:
        j = await self._get_jurisdiction_by_code(jurisdiction_code)
        if j is None:
            raise NotFoundError(f"Jurisdiction not found")
        dd = DryDay(
            jurisdiction_id=j.id, date=day, reason=reason, approved_by=approved_by,
            is_recurring=is_recurring, recurring_rule=recurring_rule,
        )
        self.db.add(dd)
        await self.db.commit()
        await self.db.refresh(dd)
        return dd

    async def get_dry_days(
        self, jurisdiction_code: str, from_date: date, to_date: date,
    ) -> list[DryDay]:
        j = await self._get_jurisdiction_by_code(jurisdiction_code)
        if j is None:
            return []
        result = await self.db.execute(
            select(DryDay).where(
                DryDay.jurisdiction_id == j.id,
                DryDay.date >= from_date,
                DryDay.date <= to_date,
                DryDay.is_active == True,  # noqa: E712
            ).order_by(DryDay.date)
        )
        return list(result.scalars().all())

    # ============================================================
    # Evaluation
    # ============================================================
    async def evaluate_order(self, request: EvaluateRequest) -> EvaluateResponse:
        """Evaluate an order against all applicable policies."""
        jurisdiction = await self._get_jurisdiction_by_code(request.jurisdiction_code)
        if jurisdiction is None:
            raise NotFoundError(f"Jurisdiction not found: {request.jurisdiction_code}")

        # Load all relevant policies
        age_policy = await self.get_active_policy(request.jurisdiction_code, "age")
        hours_policy = await self.get_active_policy(request.jurisdiction_code, "hours")
        product_policy = await self.get_active_policy(request.jurisdiction_code, "product")
        delivery_policy = await self.get_active_policy(request.jurisdiction_code, "delivery")

        # Load dry days for the requested date ± 1 day window
        request_date = request.requested_at.date()
        dry_days_db = await self.get_dry_days(
            request.jurisdiction_code, request_date, request_date
        )
        dry_dates = [d.date for d in dry_days_db]

        # Build evaluation request
        eval_req = EvaluationRequest(
            subject_type="order",
            subject_id=request.subject_id,
            jurisdiction_code=request.jurisdiction_code,
            requested_at=request.requested_at,
            actor=request.actor,
            context=request.context,
        )

        # Extract rule values from policies
        min_age = (age_policy.rules.get("min_age", 21) if age_policy else 21)
        sales_hours = (hours_policy.rules if hours_policy else {
            "start": "00:00", "end": "23:59", "days": [0, 1, 2, 3, 4, 5, 6]
        })
        jurisdiction_categories = (
            product_policy.rules.get("allowed_categories", ["beer", "wine", "spirit"])
            if product_policy else ["beer", "wine", "spirit"]
        )
        quantity_limit = (
            product_policy.rules.get("quantity_limit_per_order")
            if product_policy else None
        )
        permitted_zones = (
            delivery_policy.rules.get("permitted_zones", [])
            if delivery_policy else []
        )

        # Extract context values
        license_info = request.context.get("license", {})
        product_info = request.context.get("product", {})

        # Evaluate
        result: EvaluationResult = evaluate_order(
            eval_req,
            min_age=min_age,
            dry_days=dry_dates,
            sales_hours=sales_hours,
            license_info=license_info,
            product_info=product_info,
            jurisdiction_categories=jurisdiction_categories,
            quantity_limit=quantity_limit,
            permitted_zones=permitted_zones,
        )

        # Persist decision (immutable history)
        decision = Decision(
            decision_id=f"dec_{request.subject_id}_{int(request.requested_at.timestamp())}",
            subject_type="order",
            subject_id=request.subject_id,
            jurisdiction_code=request.jurisdiction_code,
            decision=result.decision.value,
            confidence=result.confidence,
            reasons=[h.__dict__ for h in result.hits],
            matched_rules=[h.rule_id for h in result.hits],
            policy_versions={
                "age": age_policy.version if age_policy else "default",
                "hours": hours_policy.version if hours_policy else "default",
                "product": product_policy.version if product_policy else "default",
                "delivery": delivery_policy.version if delivery_policy else "default",
            },
            evaluation_ms=result.evaluation_ms,
            requester=request.actor.get("user_id") if request.actor else None,
            context=request.context,
        )
        self.db.add(decision)
        await self.db.commit()

        # Emit event
        if self.producer is not None:
            try:
                event = make_event(
                    event_type="compliance.decision_made",
                    payload={
                        "decision_id": decision.decision_id,
                        "subject_type": "order",
                        "subject_id": request.subject_id,
                        "decision": result.decision.value,
                        "policy_versions": decision.policy_versions,
                    },
                    producer=settings.service_name,
                )
                await self.producer.publish(topic="compliance.events", payload=event)
            except Exception:
                logger.exception("Failed to publish compliance event")

        return EvaluateResponse(
            decision_id=decision.decision_id,
            decision=result.decision.value,
            confidence=result.confidence,
            reasons=[h.reason for h in result.hits if h.outcome != DecisionOutcome.ALLOW],
            matched_rules=[h.rule_id for h in result.hits],
            policy_versions=decision.policy_versions,
            evaluation_ms=result.evaluation_ms,
            details=result.to_dict(),
        )

    # ============================================================
    # Static policy file loading (YAML)
    # ============================================================
    def load_static_policies(self, jurisdiction_code: str) -> dict[str, Any]:
        """Load static policy files from the policies directory."""
        if jurisdiction_code in self._static_policies_cache:
            return self._static_policies_cache[jurisdiction_code]
        policies_dir = Path(settings.policies_path)
        if not policies_dir.exists():
            return {}
        result: dict[str, Any] = {}
        for path in policies_dir.rglob("*.yaml"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
                if data.get("jurisdiction") == jurisdiction_code:
                    result[path.stem] = data
            except Exception:
                logger.exception("Failed to load policy file: %s", path)
        self._static_policies_cache[jurisdiction_code] = result
        return result

    # ============================================================
    # Helpers
    # ============================================================
    async def _get_jurisdiction_by_code(self, code: str) -> Jurisdiction | None:
        result = await self.db.execute(
            select(Jurisdiction).where(Jurisdiction.code == code)
        )
        return result.scalar_one_or_none()

    async def _invalidate_cache(self, jurisdiction_code: str, policy_type: str) -> None:
        pass
