"""
Zero-downtime Policy Versioning & Migration Engine.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from faccp_common.exceptions import ConflictError, NotFoundError, ValidationError
from faccp_common.logging import get_logger
from app.db.models import Jurisdiction, Policy, PolicyMigration, PolicyTestCase
from app.services.rule_engine import RuleEngine

logger = get_logger(__name__)


class PolicyMigrationService:

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.engine = RuleEngine()

    async def prepare_migration(
        self,
        *,
        jurisdiction_code: str,
        policy_type: str,
        from_version: str,
        to_version: str,
        new_rules: dict[str, Any],
        prepared_by: str,
        test_cases: list[dict[str, Any]] | None = None,
    ) -> PolicyMigration:
        num = f"MIG-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        migration = PolicyMigration(
            id=str(uuid.uuid4()),
            migration_number=num,
            jurisdiction_code=jurisdiction_code,
            policy_type=policy_type,
            from_version=from_version,
            to_version=to_version,
            rules_diff={"new_rules": new_rules},
            status="DRAFT",
            prepared_by=prepared_by,
        )
        self.db.add(migration)
        await self.db.commit()

        if test_cases:
            for tc in test_cases:
                tc_obj = PolicyTestCase(
                    id=str(uuid.uuid4()),
                    migration_id=migration.id,
                    name=tc["name"],
                    input_context=tc["input_context"],
                    expected_decision=tc["expected_decision"],
                )
                self.db.add(tc_obj)
            await self.db.commit()

        return migration

    async def run_test_suite(self, migration_id: str) -> PolicyMigration:
        migration = await self._get_migration(migration_id)
        result = await self.db.execute(
            select(PolicyTestCase).where(PolicyTestCase.migration_id == migration_id)
        )
        cases = list(result.scalars().all())

        passed_count = 0
        failed_count = 0
        rules = migration.rules_diff.get("new_rules", {})

        for case in cases:
            try:
                dec = self.engine.evaluate(context=case.input_context, custom_rules=rules)
                case.actual_decision = dec.decision.value
                case.passed = (dec.decision.value == case.expected_decision)
                if case.passed:
                    passed_count += 1
                else:
                    failed_count += 1
            except Exception as e:
                case.passed = False
                case.error = str(e)
                failed_count += 1

        migration.tests_total = len(cases)
        migration.tests_passed = passed_count
        migration.tests_failed = failed_count
        migration.status = "TESTED_PASSED" if failed_count == 0 else "TESTED_FAILED"
        await self.db.commit()
        return migration

    async def activate_migration(self, migration_id: str, approver_id: str) -> PolicyMigration:
        migration = await self._get_migration(migration_id)
        if migration.status not in ("DRAFT", "TESTED_PASSED"):
            raise ConflictError(f"Cannot activate migration in status {migration.status}")

        result = await self.db.execute(
            select(Jurisdiction).where(Jurisdiction.code == migration.jurisdiction_code)
        )
        j = result.scalar_one_or_none()
        if j is None:
            raise NotFoundError(f"Jurisdiction {migration.jurisdiction_code} not found")

        # Deactivate old policies of this type
        old_policies = await self.db.execute(
            select(Policy).where(
                Policy.jurisdiction_id == j.id,
                Policy.policy_type == migration.policy_type,
                Policy.is_active == True,
            )
        )
        for p in old_policies.scalars().all():
            p.is_active = False

        # Create new policy version
        new_policy = Policy(
            id=str(uuid.uuid4()),
            jurisdiction_id=j.id,
            policy_type=migration.policy_type,
            version=migration.to_version,
            name=f"{migration.policy_type} Policy {migration.to_version}",
            rules=migration.rules_diff.get("new_rules", {}),
            effective_from=datetime.now(timezone.utc).date(),
            is_active=True,
            approved_by=approver_id,
            approved_at=datetime.now(timezone.utc),
            checksum=uuid.uuid4().hex,
        )
        self.db.add(new_policy)

        migration.status = "ACTIVE"
        migration.approved_by = approver_id
        migration.activated_at = datetime.now(timezone.utc)
        await self.db.commit()
        return migration

    async def rollback_migration(self, migration_id: str, actor_id: str, reason: str) -> PolicyMigration:
        migration = await self._get_migration(migration_id)
        if migration.status != "ACTIVE":
            raise ConflictError("Can only rollback an active migration")

        result = await self.db.execute(
            select(Jurisdiction).where(Jurisdiction.code == migration.jurisdiction_code)
        )
        j = result.scalar_one_or_none()
        if j is None:
            raise NotFoundError(f"Jurisdiction {migration.jurisdiction_code} not found")

        # Deactivate current version
        cur_policies = await self.db.execute(
            select(Policy).where(
                Policy.jurisdiction_id == j.id,
                Policy.policy_type == migration.policy_type,
                Policy.version == migration.to_version,
            )
        )
        for p in cur_policies.scalars().all():
            p.is_active = False

        # Re-activate previous version
        prev_policies = await self.db.execute(
            select(Policy).where(
                Policy.jurisdiction_id == j.id,
                Policy.policy_type == migration.policy_type,
                Policy.version == migration.from_version,
            )
        )
        for p in prev_policies.scalars().all():
            p.is_active = True

        migration.status = "ROLLED_BACK"
        migration.rolled_back_at = datetime.now(timezone.utc)
        migration.rollback_reason = reason
        await self.db.commit()
        return migration

    async def _get_migration(self, migration_id: str) -> PolicyMigration:
        result = await self.db.execute(
            select(PolicyMigration).where(PolicyMigration.id == migration_id)
        )
        m = result.scalar_one_or_none()
        if m is None:
            raise NotFoundError("Migration not found")
        return m
