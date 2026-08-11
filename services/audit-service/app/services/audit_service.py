"""
Audit service — append-only, hash-chained event store.

Key properties:
- Events are NEVER updated or deleted from the application
- Each event contains a SHA-256 hash of itself + the previous event's hash
- Sequence numbers are monotonically increasing
- Chain integrity can be verified at any time
- Exports are themselves audited
"""

from __future__ import annotations

import hashlib
import json
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
from app.db.models import AuditEvent, AuditExport

logger = get_logger(__name__)
settings = get_settings()


def _canonical_payload(payload: dict[str, Any]) -> str:
    """Deterministic JSON for hashing."""
    return json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))


def _compute_event_hash(
    *,
    event_id: str,
    sequence: int,
    actor_id: str | None,
    action: str,
    resource_type: str,
    resource_id: str | None,
    result: str,
    occurred_at: datetime,
    payload: dict[str, Any],
    previous_hash: str,
) -> str:
    """Compute SHA-256 hash for an event including the previous event's hash."""
    hash_input = {
        "event_id": event_id,
        "sequence": sequence,
        "actor_id": actor_id,
        "action": action,
        "resource_type": resource_type,
        "resource_id": resource_id,
        "result": result,
        "occurred_at": occurred_at.isoformat(),
        "payload": payload,
        "previous_hash": previous_hash,
    }
    canonical = _canonical_payload(hash_input)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


class AuditService:
    """Append-only audit event store."""

    def __init__(self, db: AsyncSession, producer: EventProducer | None = None) -> None:
        self.db = db
        self.producer = producer

    # ============================================================
    # Append event
    # ============================================================
    async def append(
        self,
        *,
        actor_id: str | None = None,
        actor_type: str,
        actor_role: str | None = None,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        event_type: str,
        result: str,
        severity: str = "info",
        service_name: str,
        correlation_id: str | None = None,
        causation_id: str | None = None,
        policy_version: str | None = None,
        jurisdiction_code: str | None = None,
        description: str | None = None,
        error_code: str | None = None,
        payload: dict[str, Any] | None = None,
        before_state: dict[str, Any] | None = None,
        after_state: dict[str, Any] | None = None,
        actor_ip: str | None = None,
        actor_user_agent: str | None = None,
        session_id: str | None = None,
        organization_id: str | None = None,
        occurred_at: datetime | None = None,
        duration_ms: int | None = None,
    ) -> AuditEvent:
        """Append a new event to the chain. Never updates existing events."""
        res = await self.db.execute(
            select(AuditEvent).order_by(AuditEvent.sequence_number.desc()).limit(1)
        )
        prev = res.scalar_one_or_none()
        previous_hash = prev.event_hash if prev else ("0" * 64)
        sequence = (prev.sequence_number + 1) if prev else 1

        event_id = f"aud_{uuid.uuid4().hex[:24]}"
        occurred = occurred_at or datetime.now(timezone.utc)
        payload_dict = payload or {}

        event_hash = _compute_event_hash(
            event_id=event_id,
            sequence=sequence,
            actor_id=actor_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            result=result,
            occurred_at=occurred,
            payload=payload_dict,
            previous_hash=previous_hash,
        )

        event = AuditEvent(
            event_id=event_id,
            sequence_number=sequence,
            actor_id=actor_id,
            actor_type=actor_type,
            actor_role=actor_role,
            actor_ip=actor_ip,
            actor_user_agent=actor_user_agent,
            session_id=session_id,
            organization_id=organization_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            event_type=event_type,
            description=description,
            result=result,
            severity=severity,
            error_code=error_code,
            service_name=service_name,
            correlation_id=correlation_id,
            causation_id=causation_id,
            policy_version=policy_version,
            jurisdiction_code=jurisdiction_code,
            payload=payload_dict,
            before_state=before_state,
            after_state=after_state,
            occurred_at=occurred,
            duration_ms=duration_ms,
            previous_hash=previous_hash,
            event_hash=event_hash,
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)

        if self.producer is not None:
            try:
                kafka_event = make_event(
                    event_type="audit.event_appended",
                    payload={
                        "audit_event_id": event_id,
                        "sequence": sequence,
                        "actor_id": actor_id,
                        "action": action,
                        "resource_type": resource_type,
                        "resource_id": resource_id,
                        "result": result,
                        "service_name": service_name,
                        "event_hash": event_hash,
                    },
                    producer=service_name,
                    correlation_id=correlation_id,
                )
                await self.producer.publish(topic="audit.events", payload=kafka_event)
            except Exception:
                logger.exception("Failed to publish audit event to Kafka")

        return event

    # ============================================================
    # Query
    # ============================================================
    async def search(
        self,
        *,
        actor_id: str | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        service_name: str | None = None,
        result: str | None = None,
        from_time: datetime | None = None,
        to_time: datetime | None = None,
        correlation_id: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[AuditEvent], int]:
        q = select(AuditEvent)
        if actor_id:
            q = q.where(AuditEvent.actor_id == actor_id)
        if action:
            q = q.where(AuditEvent.action == action)
        if resource_type:
            q = q.where(AuditEvent.resource_type == resource_type)
        if resource_id:
            q = q.where(AuditEvent.resource_id == resource_id)
        if service_name:
            q = q.where(AuditEvent.service_name == service_name)
        if result:
            q = q.where(AuditEvent.result == result)
        if from_time:
            q = q.where(AuditEvent.occurred_at >= from_time)
        if to_time:
            q = q.where(AuditEvent.occurred_at <= to_time)
        if correlation_id:
            q = q.where(AuditEvent.correlation_id == correlation_id)
        q = q.order_by(AuditEvent.sequence_number.desc())
        offset = (page - 1) * page_size
        q = q.offset(offset).limit(page_size)

        res = await self.db.execute(q)
        events = list(res.scalars().all())

        count_q = select(AuditEvent)
        if actor_id:
            count_q = count_q.where(AuditEvent.actor_id == actor_id)
        if resource_id:
            count_q = count_q.where(AuditEvent.resource_id == resource_id)
        count_result = await self.db.execute(count_q)
        total = len(count_result.scalars().all())

        return events, total

    # ============================================================
    # Chain integrity verification
    # ============================================================
    async def verify_chain(
        self, from_sequence: int = 1, to_sequence: int | None = None,
    ) -> dict[str, Any]:
        """Verify the integrity of the hash chain. Returns verification report."""
        q = select(AuditEvent).where(
            AuditEvent.sequence_number >= from_sequence
        ).order_by(AuditEvent.sequence_number.asc())
        if to_sequence is not None:
            q = q.where(AuditEvent.sequence_number <= to_sequence)

        res = await self.db.execute(q)
        events = list(res.scalars().all())

        expected_previous = "0" * 64
        expected_sequence = from_sequence
        verified = 0
        broken_at: list[dict[str, Any]] = []

        for event in events:
            if event.sequence_number != expected_sequence:
                broken_at.append({
                    "sequence": event.sequence_number,
                    "issue": "sequence_gap",
                    "expected": expected_sequence,
                })

            if event.previous_hash != expected_previous:
                broken_at.append({
                    "sequence": event.sequence_number,
                    "issue": "previous_hash_mismatch",
                    "event_id": event.event_id,
                })

            recomputed = _compute_event_hash(
                event_id=event.event_id,
                sequence=event.sequence_number,
                actor_id=event.actor_id,
                action=event.action,
                resource_type=event.resource_type,
                resource_id=event.resource_id,
                result=event.result,
                occurred_at=event.occurred_at,
                payload=event.payload or {},
                previous_hash=event.previous_hash,
            )
            if recomputed != event.event_hash:
                broken_at.append({
                    "sequence": event.sequence_number,
                    "issue": "hash_mismatch",
                    "event_id": event.event_id,
                    "stored_hash": event.event_hash,
                    "computed_hash": recomputed,
                })

            expected_previous = event.event_hash
            expected_sequence = event.sequence_number + 1
            verified += 1

        return {
            "verified_count": verified,
            "broken_count": len(broken_at),
            "is_intact": len(broken_at) == 0,
            "broken_events": broken_at[:100],
            "from_sequence": from_sequence,
            "to_sequence": to_sequence or (events[-1].sequence_number if events else None),
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }
