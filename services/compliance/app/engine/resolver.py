"""Policy resolver engine component."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..domain.enums import PolicyStatus
from ..models.policy import CompliancePolicy


class PolicyResolver:
    """Resolves active compliance policy for a jurisdiction and effective timestamp."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def resolve(
        self,
        jurisdiction_id: str | uuid.UUID,
        timestamp: datetime | None = None,
    ) -> CompliancePolicy | None:
        """Query active policy for given jurisdiction_id and timestamp."""
        jid_str = str(jurisdiction_id)
        eval_time = timestamp or datetime.now(timezone.utc)

        stmt = (
            select(CompliancePolicy)
            .where(
                CompliancePolicy.jurisdiction_id == jid_str,
                CompliancePolicy.status == PolicyStatus.ACTIVE,
                CompliancePolicy.effective_from <= eval_time,
                or_(
                    CompliancePolicy.effective_until.is_(None),
                    CompliancePolicy.effective_until >= eval_time,
                ),
            )
            .order_by(CompliancePolicy.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()
