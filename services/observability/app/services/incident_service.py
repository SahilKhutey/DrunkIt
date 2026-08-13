from datetime import datetime, timezone
from uuid import uuid4

from services.observability.app.engine.incident_engine import IncidentEngine


class IncidentService:

    def __init__(self, incident_engine: IncidentEngine | None = None):
        self.incident_engine = incident_engine or IncidentEngine()
        self.incidents: dict[str, dict] = {}

    async def create_incident(
        self,
        service: str,
        title: str,
        severity: str = "HIGH",
        assigned_to: str | None = None,
    ) -> dict:

        inc_id = str(uuid4())
        record = {
            "id": inc_id,
            "incident_code": f"INC-{uuid4().hex[:8]}",
            "title": title,
            "severity": severity,
            "status": "OPEN",
            "service": service,
            "assigned_to": assigned_to,
            "started_at": datetime.now(timezone.utc),
            "resolved_at": None,
        }
        self.incidents[inc_id] = record
        return record

    async def get_active_incidents(self) -> list[dict]:
        return [i for i in self.incidents.values() if i["status"] not in ("RESOLVED", "CLOSED")]

    async def get_incident(self, incident_id: str) -> dict | None:
        return self.incidents.get(incident_id)

    async def acknowledge_incident(self, incident_id: str, user_id: str = "operator") -> dict:
        inc = self.incidents.get(incident_id)
        if not inc:
            raise ValueError("INCIDENT_NOT_FOUND")
        inc["status"] = "ACKNOWLEDGED"
        inc["assigned_to"] = user_id
        return inc

    async def resolve_incident(self, incident_id: str) -> dict:
        inc = self.incidents.get(incident_id)
        if not inc:
            raise ValueError("INCIDENT_NOT_FOUND")
        inc["status"] = "RESOLVED"
        inc["resolved_at"] = datetime.now(timezone.utc)
        return inc
