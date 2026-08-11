"""
Enhanced risk service — combines deterministic rules, ML, and anomaly detection.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.events import make_event
from faccp_common.exceptions import NotFoundError
from faccp_common.kafka_client import EventProducer
from faccp_common.logging import get_logger

from app.config import get_settings
from app.db.models import FraudCase, RiskProfile, RiskSignal
from app.ml.fraud_detector import get_fraud_ensemble
from app.schemas.risk import (
    EnhancedEvaluateRequest, EnhancedEvaluateResponse,
)

logger = get_logger(__name__)
settings = get_settings()


def level_from_score(score: int) -> str:
    if score < 20: return "LOW"
    if score < 50: return "MEDIUM"
    if score < 80: return "HIGH"
    return "CRITICAL"


class RiskServiceV2:

    def __init__(self, db: AsyncSession, producer: EventProducer | None = None) -> None:
        self.db = db
        self.producer = producer
        self.fraud_ensemble = get_fraud_ensemble()

    async def evaluate_v2(self, payload: EnhancedEvaluateRequest) -> EnhancedEvaluateResponse:
        rule_score = 10 if payload.context.get("vpn_detected") else 0

        ensemble_result = self.fraud_ensemble.evaluate(
            context=payload.context,
            history=payload.history or [],
            rule_score=min(rule_score / 100.0, 1.0),
            user_id=payload.subject_id if payload.subject_type == "consumer" else None,
        )

        final_score = ensemble_result["final_score"] * 100
        level = level_from_score(int(final_score))

        profile = await self._upsert_profile(
            payload.subject_type,
            payload.subject_id,
            int(final_score),
            level,
            ensemble_result,
            payload.context,
        )

        if level in ("HIGH", "CRITICAL"):
            await self._maybe_open_fraud_case(payload, int(final_score), level, ensemble_result)

        await self.db.commit()

        if self.producer:
            try:
                await self.producer.publish("risk.events", make_event(
                    "risk.evaluated_v2", {
                        "subject_type": payload.subject_type,
                        "subject_id": payload.subject_id,
                        "final_score": int(final_score),
                        "level": level,
                        "ml_probability": ensemble_result["ml_probability"],
                        "is_anomaly": ensemble_result["is_anomaly"],
                    }, producer=settings.service_name
                ))
            except Exception:
                pass

        return EnhancedEvaluateResponse(
            subject_type=payload.subject_type,
            subject_id=payload.subject_id,
            final_score=int(final_score),
            level=level,
            breakdown={
                "rule_score": ensemble_result["rule_score"],
                "anomaly_score": ensemble_result["anomaly_score"],
                "ml_probability": ensemble_result["ml_probability"],
                "ato_score": ensemble_result["ato_score"],
            },
            is_anomaly=ensemble_result["is_anomaly"],
            top_contributors=ensemble_result["top_contributors"],
            ato_signals=ensemble_result["ato_signals"],
            profile_id=profile.id,
            evaluated_at=profile.last_evaluated_at,
            explanation=self._build_explanation(ensemble_result, level),
        )

    def _build_explanation(self, result: dict, level: str) -> str:
        parts = [f"Risk level: {level} (score: {result['final_score']:.2f})"]
        if result["is_anomaly"]:
            parts.append("Statistical anomaly detected in behavioral patterns.")
        if result["ml_probability"] > 0.7:
            parts.append("ML model indicates high fraud probability.")
        if result["ato_signals"]:
            parts.append(f"Account takeover signals: {', '.join(result['ato_signals'])}")
        for c in result["top_contributors"][:3]:
            parts.append(
                f" • {c['feature']}: {c['value']:.2f} (contribution: {c['contribution']:.3f})"
            )
        return "\n".join(parts)

    async def _upsert_profile(
        self, subject_type, subject_id, score, level, ensemble_result, context
    ) -> RiskProfile:
        result = await self.db.execute(select(RiskProfile).where(
            RiskProfile.subject_type == subject_type,
            RiskProfile.subject_id == subject_id
        ))
        profile = result.scalar_one_or_none()
        signals = (
            [{"type": "ml", "probability": ensemble_result["ml_probability"]}]
            + ([{"type": "ato", "signals": ensemble_result["ato_signals"]}] if ensemble_result["ato_signals"] else [])
        )
        if profile is None:
            profile = RiskProfile(id=str(uuid.uuid4()), subject_type=subject_type, subject_id=subject_id)
            self.db.add(profile)
        profile.risk_score = score
        profile.risk_level = level
        profile.confidence = 0.85
        profile.signals = signals
        profile.features = {
            "ensemble": ensemble_result,
            "context": context,
        }
        profile.last_evaluated_at = datetime.now(timezone.utc)
        await self.db.flush()
        return profile

    async def _maybe_open_fraud_case(self, payload, score, level, ensemble_result):
        case_number = f"FRD-{datetime.now(timezone.utc).strftime('%Y%m')}-{uuid.uuid4().hex[:8].upper()}"
        case = FraudCase(
            id=str(uuid.uuid4()),
            case_number=case_number,
            subject_type=payload.subject_type,
            subject_id=payload.subject_id,
            severity=level,
            risk_score=score,
            title=f"Auto-opened: {level} risk for {payload.subject_type}",
            description=f"ML score: {ensemble_result['ml_probability']:.2f}, ATO: {ensemble_result['ato_score']:.2f}",
            related_signals=ensemble_result.get("ato_signals", []),
        )
        self.db.add(case)
