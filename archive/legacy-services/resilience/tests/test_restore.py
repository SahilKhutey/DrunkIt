import pytest
from services.resilience.app.services.restore_service import RestoreService


@pytest.mark.asyncio
async def test_restore_operation():
    svc = RestoreService()
    res = await svc.restore_backup("backup-test-100", "postgresql")
    assert res["status"] == "COMPLETED"
    assert res["backup_id"] == "backup-test-100"
