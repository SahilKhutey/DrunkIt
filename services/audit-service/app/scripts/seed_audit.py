"""Seed sample cryptographic audit log entries."""

from __future__ import annotations

import asyncio
from sqlalchemy import select

from app.config import get_settings
from app.db.base import Base
from app.db.models import CryptographicAuditEntry
from app.schemas.audit import AuditEntryCreate
from app.services.audit_service import AuditService
from faccp_common.database import init_engine, session_scope

SAMPLE_LOGS = [
    {
        "event_type": "identity.user_registered",
        "actor_id": "usr_consumer_seed_101",
        "actor_role": "CONSUMER",
        "resource_type": "USER",
        "resource_id": "usr_consumer_seed_101",
        "payload_json": '{"phone": "+919876543210", "state": "KA"}',
    },
    {
        "event_type": "order.created",
        "actor_id": "usr_consumer_seed_101",
        "actor_role": "CONSUMER",
        "resource_type": "ORDER",
        "resource_id": "ORD-20260812-9A8B",
        "payload_json": '{"amount_inr": 2850.0, "store_id": "STR_KA_BLR_001"}',
    },
]


async def seed() -> None:
    settings = get_settings()
    init_engine(settings.database_url)
    async with session_scope() as session:
        service = AuditService(db=session)
        for log in SAMPLE_LOGS:
            existing = await session.execute(
                select(CryptographicAuditEntry).where(
                    CryptographicAuditEntry.resource_id == log["resource_id"],
                    CryptographicAuditEntry.event_type == log["event_type"],
                )
            )
            if existing.scalar_one_or_none() is None:
                entry = await service.log_event(AuditEntryCreate(**log))
                print(f"  Audit entry seeded: #{entry.sequence_number} ({entry.event_type}) -> Hash: {entry.current_hash[:16]}...")

    print("\n[OK] Seeded cryptographic audit log entries.")


if __name__ == "__main__":
    asyncio.run(seed())
