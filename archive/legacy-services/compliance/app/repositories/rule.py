"""Compliance Rule repository."""

from __future__ import annotations

import json
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.enums import Operator, RuleType
from ..models.rule import ComplianceRule


class RuleRepository:
    """Repository handling compliance rule persistence."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_for_policy(self, policy_id: str | uuid.UUID) -> list[ComplianceRule]:
        """Fetch active compliance rules for given policy_id ordered by priority."""
        pid_str = str(policy_id)
        stmt = (
            select(ComplianceRule)
            .where(
                ComplianceRule.policy_id == pid_str,
                ComplianceRule.active.is_(True),
            )
            .order_by(ComplianceRule.priority.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self,
        policy_id: str | uuid.UUID,
        name: str,
        rule_type: RuleType,
        operator: Operator,
        field: str,
        value: dict,
        priority: int = 100,
        blocking: bool = True,
    ) -> ComplianceRule:
        """Create new compliance rule."""
        pid_str = str(policy_id)
        val_json = json.dumps(value)
        rule = ComplianceRule(
            policy_id=pid_str,
            name=name,
            rule_type=rule_type,
            operator=operator,
            field=field,
            value_json=val_json,
            priority=priority,
            blocking=blocking,
            active=True,
        )
        self.session.add(rule)
        await self.session.flush()
        return rule
