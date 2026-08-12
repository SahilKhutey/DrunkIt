"""Risk service: Real-time Fraud Detection & Risk Scoring Engine."""

from __future__ import annotations

import json
import secrets
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.communication.envelope import create_envelope
from faccp_common.communication.producer import EventProducer
from faccp_common.logging import get_logger

from app.db.models import FraudPatternRule, RiskEvaluation
from app.schemas.risk import FraudRuleCreate, RiskEvaluationRequest

logger = get_logger(__name__)


class RiskService:
    """Fraud score evaluator analyzing velocity, device anomalies, and amount thresholds."""

    def __init__(self, db: AsyncSession, producer: EventProducer | None = None) -> None:
        self.db = db
        self.producer = producer

    async def evaluate_risk(self, payload: RiskEvaluationRequest) -> RiskEvaluation:
        score = 0.05
        reasons = []

        if payload.amount_inr > 25000.0:
            score += 0.35
            reasons.append("HIGH_TRANSACTION_VALUE")

        if payload.velocity_count_1h > 3:
            score += 0.40
            reasons.append("HIGH_VELOCITY_BURST")

        if payload.is_new_device:
            score += 0.15
            reasons.append("UNRECOGNIZED_DEVICE")

        decision = "PASS"
        if score >= 0.70:
            decision = "REJECT"
        elif score >= 0.40:
            decision = "REVIEW"

        code = f"RSK-{secrets.token_hex(4).upper()}"
        eval_rec = RiskEvaluation(
            evaluation_code=code,
            entity_type=payload.entity_type,
            entity_id=payload.entity_id,
            risk_score=min(score, 1.0),
            decision=decision,
            reason_codes_json=json.dumps(reasons),
        )
        self.db.add(eval_rec)
        await self.db.commit()
        await self.db.refresh(eval_rec)

        if decision in ("REVIEW", "REJECT"):
            await self._publish("risk.flagged", {
                "evaluation_id": eval_rec.id, "entity_type": eval_rec.entity_type,
                "entity_id": eval_rec.entity_id, "score": eval_rec.risk_score, "decision": decision,
            })
        return eval_rec

    async def create_rule(self, payload: FraudRuleCreate) -> FraudPatternRule:
        rule = FraudPatternRule(
            rule_name=payload.rule_name,
            description=payload.description,
            risk_score_impact=payload.risk_score_impact,
            is_active=True,
        )
        self.db.add(rule)
        await self.db.commit()
        await self.db.refresh(rule)
        return rule

    async def list_flagged(self) -> list[RiskEvaluation]:
        result = await self.db.execute(
            select(RiskEvaluation).where(RiskEvaluation.decision.in_(["REVIEW", "REJECT"]))
            .order_by(RiskEvaluation.created_at.desc())
        )
        return list(result.scalars().all())

    async def _publish(self, event_type: str, payload: dict) -> None:
        if not self.producer:
            return
        try:
            envelope = create_envelope(event_type, payload, producer="faccp-risk")
            await self.producer.publish("risk.events", envelope)
        except Exception:
            logger.exception("event_publish_failed", event_type=event_type)
