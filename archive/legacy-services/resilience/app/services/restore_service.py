from services.resilience.app.engine.restore_engine import RestoreEngine


class RestoreService:

    def __init__(self, restore_engine: RestoreEngine | None = None):
        self.restore_engine = restore_engine or RestoreEngine()

    async def restore_backup(self, backup_id: str, resource: str = "postgresql") -> dict:
        return await self.restore_engine.restore(backup_id, resource)
