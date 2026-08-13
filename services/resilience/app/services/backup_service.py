from datetime import datetime, timezone
from services.resilience.app.engine.backup_engine import create_database_backup, verify_backup


class BackupService:

    def __init__(self):
        self.backups: dict[str, dict] = {}

    async def start_backup(self, resource: str = "postgresql") -> dict:
        b = await create_database_backup(resource=resource)
        self.backups[b["backup_id"]] = b
        return b

    async def list_backups(self) -> list[dict]:
        return list(self.backups.values())

    async def get_backup(self, backup_id: str) -> dict | None:
        return self.backups.get(backup_id)

    async def verify_backup_record(self, backup_id: str) -> dict:
        b = self.backups.get(backup_id)
        if not b:
            raise ValueError("BACKUP_NOT_FOUND")

        valid = await verify_backup(b["location"], b["checksum"])
        b["verified"] = valid
        b["verified_at"] = datetime.now(timezone.utc)
        return b
