"""Eligibility evaluation domain service."""

from __future__ import annotations

import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from faccp_platform.events.envelope import EventEnvelope, EventMetadata
from faccp_platform.events.outbox import OutboxService
from faccp_platform.events.topics import Topics

from ..domain.decision import EligibilityDecision
from ..domain.events import EligibilityEvaluatedEvent
from ..engine.context import EligibilityContext
from ..engine.engine import ComplianceEngine
from ..engine.resolver import PolicyResolver
from ..repositories.decision import DecisionRepository
from ..repositories.rule import RuleRepository


class EligibilityService:
    """Service executing compliance eligibility evaluation and audit logging."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.resolver = PolicyResolver(session)
        self.rules = RuleRepository(session)
        self.decisions = DecisionRepository(session)
        self.engine = ComplianceEngine()

    async def evaluate(
        self,
        context: EligibilityContext,
        jurisdiction_id: str | uuid.UUID,
    ) -> EligibilityDecision:
        """Evaluate compliance context for jurisdiction and persist audit decision."""
        policy = await self.resolver.resolve(
            jurisdiction_id=jurisdiction_id,
            timestamp=context.timestamp,
        )

        rules = []
        if policy is not None:
            rules = await self.rules.get_for_policy(policy.id)

        decision = self.engine.evaluate(
            context=context,
            policy=policy,
            rules=rules,
            jurisdiction_id=uuid.UUID(str(jurisdiction_id)),
        )

        # Audit persistence
        await self.decisions.save_decision(
            decision=decision,
            consumer_id=str(context.consumer.consumer_id),
            product_id=str(context.product.product_id),
            context_snapshot=context.model_dump(mode="json"),
        )

        # Transactional outbox event enqueue
        if self.session is not None:
            outbox = OutboxService(self.session)
            evaluated_event = EligibilityEvaluatedEvent(
                decision_id=str(decision.decision_id),
                consumer_id=str(context.consumer.consumer_id),
                product_id=str(context.product.product_id),
                jurisdiction_id=str(jurisdiction_id),
                status=decision.status.value,
                policy_id=str(decision.policy_id) if decision.policy_id else None,
                engine_version=decision.engine_version,
            )
            envelope = EventEnvelope(
                event_type=evaluated_event.event_type,
                metadata=EventMetadata(producer="compliance-service"),
                payload=evaluated_event.payload(),
            )
            await outbox.enqueue(topic=Topics.COMPLIANCE_EVENTS, event=envelope)

        return decision
