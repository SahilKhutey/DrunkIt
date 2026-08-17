from datetime import datetime, timezone


class RestoreEngine:

    async def restore(self, backup_id: str, resource: str = "postgresql") -> dict:
        return {
            "backup_id": backup_id,
            "resource": resource,
            "status": "COMPLETED",
            "started_at": datetime.now(timezone.utc),
            "completed_at": datetime.now(timezone.utc),
        }
