"""Compliance service: Policy Rules Engine, Dry-Day check, Age verification, Volume limits."""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.communication.envelope import create_envelope
from faccp_common.communication.producer import EventProducer
from faccp_common.exceptions import BadRequestError, ConflictError, NotFoundError
from faccp_common.logging import get_logger

from app.config import get_settings
from app.db.models import ComplianceCheck, DryDayCalendar, Policy
from app.schemas.compliance import (
    ComplianceEvaluationRequest, ComplianceEvaluationResult, DryDayCreate, PolicyCreate,
)

logger = get_logger(__name__)
settings = get_settings()


class ComplianceService:
    """Policy Rules Engine & Regulatory Evaluator."""

    def __init__(self, db: AsyncSession, producer: EventProducer | None = None) -> None:
        self.db = db
        self.producer = producer

    # ============================================================
    # POLICY MANAGEMENT
    # ============================================================
    async def create_policy(self, payload: PolicyCreate) -> Policy:
        existing = await self._get_policy_by_code(payload.code)
        if existing:
            raise ConflictError(f"Policy code {payload.code} already exists")

        policy = Policy(
            code=payload.code,
            title=payload.title,
            description=payload.description,
            jurisdiction=payload.jurisdiction,
            category=payload.category,
            effective_from=payload.effective_from,
            effective_until=payload.effective_until,
            min_purchasing_age=payload.min_purchasing_age,
            max_volume_per_transaction_ml=payload.max_volume_per_transaction_ml,
            max_volume_per_day_ml=payload.max_volume_per_day_ml,
            sales_start_time=payload.sales_start_time,
            sales_end_time=payload.sales_end_time,
            metadata_json=payload.metadata_json,
        )
        self.db.add(policy)
        await self.db.commit()
        await self.db.refresh(policy)
        return policy

    async def get_policy(self, code: str) -> Policy:
        policy = await self._get_policy_by_code(code)
        if not policy:
            raise NotFoundError(f"Policy {code} not found")
        return policy

    async def list_policies(self, jurisdiction: str | None = None) -> list[Policy]:
        stmt = select(Policy).where(Policy.is_active == True)  # noqa: E712
        if jurisdiction:
            stmt = stmt.where(Policy.jurisdiction == jurisdiction)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    # ============================================================
    # DRY DAYS
    # ============================================================
    async def add_dry_day(self, payload: DryDayCreate) -> DryDayCalendar:
        dry_day = DryDayCalendar(
            jurisdiction=payload.jurisdiction,
            dry_date=payload.dry_date,
            occasion=payload.occasion,
            is_full_day=payload.is_full_day,
            start_time=payload.start_time,
            end_time=payload.end_time,
        )
        self.db.add(dry_day)
        await self.db.commit()
        await self.db.refresh(dry_day)
        return dry_day

    async def is_dry_day(self, jurisdiction: str, dt: date) -> tuple[bool, str | None]:
        result = await self.db.execute(
            select(DryDayCalendar).where(
                DryDayCalendar.jurisdiction == jurisdiction,
                DryDayCalendar.dry_date == dt,
            )
        )
        dry = result.scalar_one_or_none()
        if dry:
            return True, dry.occasion
        return False, None

    # ============================================================
    # COMPLIANCE EVALUATION ENGINE
    # ============================================================
    async def evaluate_transaction(
        self, req: ComplianceEvaluationRequest
    ) -> ComplianceEvaluationResult:
        failures: list[str] = []
        details: dict[str, Any] = {}

        # 1. Fetch policy for jurisdiction
        policy = await self._get_active_policy(req.jurisdiction)
        if not policy:
            if settings.fail_closed:
                failures.append(f"No active policy for jurisdiction {req.jurisdiction}")

        if policy:
            # 2. Age check
            if req.consumer_age < policy.min_purchasing_age:
                failures.append(
                    f"Consumer age {req.consumer_age} is below minimum age {policy.min_purchasing_age} for {req.jurisdiction}"
                )
            details["min_age_required"] = policy.min_purchasing_age
            details["consumer_age"] = req.consumer_age

            # 3. Volume limit check
            if (
                policy.max_volume_per_transaction_ml
                and req.total_volume_ml > policy.max_volume_per_transaction_ml
            ):
                failures.append(
                    f"Transaction volume {req.total_volume_ml}ml exceeds max limit {policy.max_volume_per_transaction_ml}ml"
                )
            details["max_volume_ml"] = policy.max_volume_per_transaction_ml
            details["requested_volume_ml"] = req.total_volume_ml

            # 4. Hours check
            tx_time = req.transaction_time.time()
            if not (policy.sales_start_time <= tx_time <= policy.sales_end_time):
                failures.append(
                    f"Transaction time {tx_time.strftime('%H:%M')} outside allowed sales hours ({policy.sales_start_time.strftime('%H:%M')} - {policy.sales_end_time.strftime('%H:%M')})"
                )
            details["sales_hours"] = f"{policy.sales_start_time} - {policy.sales_end_time}"

        # 5. Dry day check
        is_dry, occasion = await self.is_dry_day(req.jurisdiction, req.transaction_time.date())
        if is_dry:
            failures.append(f"Prohibited transaction: Dry Day in {req.jurisdiction} ({occasion})")
        details["is_dry_day"] = is_dry
        details["dry_day_occasion"] = occasion

        # 6. Store License status check
        if req.store_license_status != "ACTIVE":
            failures.append(f"Store license status is {req.store_license_status} (must be ACTIVE)")
        if req.store_license_expiry and req.store_license_expiry < req.transaction_time.date():
            failures.append(f"Store license expired on {req.store_license_expiry}")

        is_compliant = len(failures) == 0

        # Persist audit record
        audit = ComplianceCheck(
            reference_id=req.reference_id,
            check_type="TRANSACTION_EVALUATION",
            jurisdiction=req.jurisdiction,
            actor_id=req.actor_id,
            is_compliant=is_compliant,
            failure_reasons=failures,
            evaluated_at=datetime.now(timezone.utc),
            details=details,
        )
        self.db.add(audit)
        await self.db.commit()

        # Publish event
        await self._publish("compliance.evaluated", {
            "reference_id": req.reference_id,
            "jurisdiction": req.jurisdiction,
            "is_compliant": is_compliant,
            "failures": failures,
        })

        return ComplianceEvaluationResult(
            reference_id=req.reference_id,
            jurisdiction=req.jurisdiction,
            is_compliant=is_compliant,
            failure_reasons=failures,
            evaluated_at=audit.evaluated_at,
            details=details,
        )

    # ============================================================
    # HELPERS
    # ============================================================
    async def _get_policy_by_code(self, code: str) -> Policy | None:
        result = await self.db.execute(select(Policy).where(Policy.code == code))
        return result.scalar_one_or_none()

    async def _get_active_policy(self, jurisdiction: str) -> Policy | None:
        result = await self.db.execute(
            select(Policy).where(
                Policy.jurisdiction == jurisdiction,
                Policy.is_active == True,  # noqa: E712
            )
        )
        return result.scalar_one_or_none()

    async def _publish(self, event_type: str, payload: dict) -> None:
        if not self.producer:
            return
        try:
            envelope = create_envelope(event_type, payload, producer="faccp-compliance")
            await self.producer.publish("compliance.events", envelope)
        except Exception:
            logger.exception("event_publish_failed", event_type=event_type)
