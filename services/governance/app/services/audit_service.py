from services.governance.app.engine.audit_engine import AuditEngine


class AuditService:

    def __init__(self, audit_engine: AuditEngine | None = None):
        self.audit_engine = audit_engine or AuditEngine()

    async def record_event(self, event_data: dict) -> dict:
        return await self.audit_engine.record(event_data)

    async def get_events(self, subject_id: str | None = None, correlation_id: str | None = None) -> list[dict]:
        res = self.audit_engine.events
        if subject_id:
            res = [e for e in res if e.get("subject_id") == subject_id]
        if correlation_id:
            res = [e for e in res if e.get("correlation_id") == correlation_id]
        return res

    async def verify_audit_chain(self) -> bool:
        return await self.audit_engine.verify_chain()
