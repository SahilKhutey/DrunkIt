"""
Master unit test for Phase D15 Disaster Recovery, Resilience & Business Continuity Engine.
"""

from __future__ import annotations

import os
import sys
import pytest

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from services.resilience.app.engine.bulkhead import Bulkhead
from services.resilience.app.engine.circuit_breaker import CircuitBreaker, call_with_breaker
from services.resilience.app.engine.degradation import ResiliencePolicyEngine
from services.resilience.app.engine.recovery_engine import RecoveryEngine
from services.resilience.app.engine.retry import RetryPolicy, backoff_delay, retry
from services.resilience.app.models.enums import CircuitState, PlatformMode, RecoveryState
from services.resilience.app.services.backup_service import BackupService
from services.resilience.app.services.continuity_service import ContinuityService
from services.resilience.app.services.failover_service import FailoverService
from services.resilience.app.services.restore_service import RestoreService


@pytest.mark.asyncio
async def test_full_d15_resilience_disaster_pipeline():
    # 1. Failure Classification & Fail-Closed Resilience Policy Engine
    pol_engine = ResiliencePolicyEngine()
    assert pol_engine.action_for("compliance") == "FAIL_CLOSED"
    assert pol_engine.action_for("security") == "FAIL_CLOSED"
    assert pol_engine.action_for("payment") == "BLOCK_NEW_TRANSACTION"
    assert pol_engine.action_for("catalog") == "READ_ONLY"

    # 2. Retry Policy with Exponential Backoff
    policy = RetryPolicy(max_attempts=3, base_delay=0.01)
    attempts = 0

    @retry(policy)
    async def sample_op():
        nonlocal attempts
        attempts += 1
        if attempts < 2:
            raise RuntimeError("NETWORK_TRANSIENT_ERROR")
        return "OK"

    res = await sample_op()
    assert res == "OK"
    assert attempts == 2

    # 3. Circuit Breaker State Machine
    breaker = CircuitBreaker(failure_threshold=1, recovery_timeout=0.01)
    assert breaker.state == CircuitState.CLOSED

    async def err_op():
        raise RuntimeError("DB_DOWN")

    with pytest.raises(RuntimeError):
        await call_with_breaker(breaker, err_op)

    assert breaker.state == CircuitState.OPEN

    # 4. Semaphore Bulkhead Worker Isolation
    bulkhead = Bulkhead(capacity=2)
    val = await bulkhead.execute(lambda: sample_op())
    assert val == "OK"

    # 5. Backup & Verification Service
    backup_svc = BackupService()
    backup = await backup_svc.start_backup("postgresql")
    assert backup["status"] == "COMPLETED"

    verified = await backup_svc.verify_backup_record(backup["backup_id"])
    assert verified["verified"] is True

    # 6. Restore Engine Operation
    restore_svc = RestoreService()
    restore_res = await restore_svc.restore_backup(backup["backup_id"])
    assert restore_res["status"] == "COMPLETED"

    # 7. Recovery State Machine Execution
    recovery_engine = RecoveryEngine()
    rec_res = await recovery_engine.recover("order-service")
    assert rec_res["final_state"] == RecoveryState.COMPLETE.value

    # 8. Health-Gated Failover Service
    failover_svc = FailoverService()
    failover_res = await failover_svc.execute_failover("order-service", "region-a", "region-b")
    assert failover_res["active"] == "region-b"

    # 9. Emergency Mode Controller & Business Continuity Audit
    continuity_svc = ContinuityService()
    status_before = await continuity_svc.get_status()
    assert status_before["platform_mode"] == PlatformMode.NORMAL.value

    enable_rec = await continuity_svc.enable_emergency(actor="sysadmin-surat", reason="REGIONAL_OUTAGE")
    assert enable_rec["action"] == "EMERGENCY_ACTIVATE"

    status_after = await continuity_svc.get_status()
    assert status_after["platform_mode"] == PlatformMode.EMERGENCY.value
