import pytest
from services.resilience.app.services.backup_service import BackupService


@pytest.mark.asyncio
async def test_backup_creation_and_verification():
    svc = BackupService()
    b = await svc.start_backup("postgresql")
    assert b["status"] == "COMPLETED"
    assert b["backup_id"].startswith("backup-")

    verified = await svc.verify_backup_record(b["backup_id"])
    assert verified["verified"] is True
