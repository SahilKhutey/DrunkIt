"""Eligibility decision audit repository."""

from __future__ import annotations

import json
import uuid
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.decision import EligibilityDecision
from ..models.decision import EligibilityDecisionModel


class DecisionRepository:
    """Repository persisting eligibility decision audit records."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, decision_id: str | uuid.UUID) -> EligibilityDecisionModel | None:
        """Fetch decision record by ID."""
        did_str = str(decision_id)
        result = await self.session.execute(
            select(EligibilityDecisionModel).where(EligibilityDecisionModel.id == did_str)
        )
        return result.scalar_one_or_none()

    async def save_decision(
        self,
        decision: EligibilityDecision,
        consumer_id: str | uuid.UUID,
        product_id: str | uuid.UUID,
        context_snapshot: dict[str, Any],
    ) -> EligibilityDecisionModel:
        """Persist eligibility decision audit record."""
        record = EligibilityDecisionModel(
            id=str(decision.decision_id),
            consumer_id=str(consumer_id),
            product_id=str(product_id),
            jurisdiction_id=str(decision.jurisdiction_id),
            policy_id=str(decision.policy_id) if decision.policy_id else None,
            status=decision.status,
            reasons_json=json.dumps(decision.reasons),
            evaluated_rules_json=json.dumps([r.model_dump(mode="json") for r in decision.results]),
            context_snapshot_json=json.dumps(context_snapshot),
            engine_version=decision.engine_version,
        )
        self.session.add(record)
        await self.session.flush()
        return record
