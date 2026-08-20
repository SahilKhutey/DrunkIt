"""Development compliance policy seeder."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from .domain.enums import Operator, PolicyStatus, RuleType
from .models.policy import CompliancePolicy
from .models.rule import ComplianceRule


async def seed_demo_policy(
    session: AsyncSession,
    jurisdiction_id: str | uuid.UUID,
) -> CompliancePolicy:
    """Seed development alcohol compliance policy into database."""
    policy = CompliancePolicy(
        id=str(uuid.uuid4()),
        jurisdiction_id=str(jurisdiction_id),
        name="Development Alcohol Policy",
        version="1.0.0",
        status=PolicyStatus.ACTIVE,
        effective_from=datetime(2020, 1, 1, tzinfo=timezone.utc),
    )
    session.add(policy)
    await session.flush()

    rules = [
        ComplianceRule(
            id=str(uuid.uuid4()),
            policy_id=policy.id,
            name="Minimum age",
            rule_type=RuleType.AGE,
            operator=Operator.GTE,
            field="consumer.age",
            value_json='{"value": 21}',
            priority=10,
            blocking=True,
            active=True,
        ),
        ComplianceRule(
            id=str(uuid.uuid4()),
            policy_id=policy.id,
            name="Consumer verification",
            rule_type=RuleType.VERIFICATION,
            operator=Operator.EQ,
            field="consumer.verified",
            value_json='{"value": true}',
            priority=20,
            blocking=True,
            active=True,
        ),
        ComplianceRule(
            id=str(uuid.uuid4()),
            policy_id=policy.id,
            name="Maximum demo quantity",
            rule_type=RuleType.QUANTITY,
            operator=Operator.LTE,
            field="product.quantity",
            value_json='{"value": 2}',
            priority=30,
            blocking=True,
            active=True,
        ),
    ]
    session.add_all(rules)
    await session.commit()
    return policy
