"""Audit service: Cryptographic Hash Chain Audit Ledger."""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from faccp_common.logging import get_logger

from app.db.models import CryptographicAuditEntry
from app.schemas.audit import AuditEntryCreate, ChainVerificationResponse

logger = get_logger(__name__)

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"


def compute_hash(prev_hash: str, event_type: str, actor_id: str, resource_id: str, payload_json: str) -> str:
    raw = f"{prev_hash}:{event_type}:{actor_id}:{resource_id}:{payload_json}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class AuditService:
    """Tamper-evident SHA256 cryptographic audit chain engine."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def log_event(self, payload: AuditEntryCreate) -> CryptographicAuditEntry:
        # Fetch latest entry to get previous_hash
        result = await self.db.execute(
            select(CryptographicAuditEntry).order_by(CryptographicAuditEntry.sequence_number.desc()).limit(1)
        )
        latest = result.scalar_one_or_none()

        prev_hash = latest.current_hash if latest else GENESIS_HASH
        curr_hash = compute_hash(
            prev_hash, payload.event_type, payload.actor_id, payload.resource_id, payload.payload_json
        )

        entry = CryptographicAuditEntry(
            event_id=f"EVT_{secrets.token_hex(8).upper()}",
            event_type=payload.event_type,
            actor_id=payload.actor_id,
            actor_role=payload.actor_role,
            resource_type=payload.resource_type,
            resource_id=payload.resource_id,
            payload_json=payload.payload_json,
            previous_hash=prev_hash,
            current_hash=curr_hash,
        )
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def verify_chain(self) -> ChainVerificationResponse:
        result = await self.db.execute(
            select(CryptographicAuditEntry).order_by(CryptographicAuditEntry.sequence_number.asc())
        )
        entries = list(result.scalars().all())

        if not entries:
            return ChainVerificationResponse(is_valid=True, total_entries=0, message="Audit chain is empty")

        expected_prev = GENESIS_HASH
        for entry in entries:
            if entry.previous_hash != expected_prev:
                return ChainVerificationResponse(
                    is_valid=False, total_entries=len(entries), corrupted_sequence=entry.sequence_number,
                    message=f"Hash chain broken at sequence {entry.sequence_number}"
                )
            recalculated = compute_hash(
                expected_prev, entry.event_type, entry.actor_id, entry.resource_id, entry.payload_json
            )
            if recalculated != entry.current_hash:
                return ChainVerificationResponse(
                    is_valid=False, total_entries=len(entries), corrupted_sequence=entry.sequence_number,
                    message=f"Payload tamper detected at sequence {entry.sequence_number}"
                )
            expected_prev = entry.current_hash

        return ChainVerificationResponse(
            is_valid=True, total_entries=len(entries), message="Cryptographic hash chain is valid and untampered"
        )

    async def list_logs(self, limit: int = 50) -> list[CryptographicAuditEntry]:
        result = await self.db.execute(
            select(CryptographicAuditEntry).order_by(CryptographicAuditEntry.sequence_number.desc()).limit(limit)
        )
        return list(result.scalars().all())
