from datetime import datetime, timezone
from uuid import uuid4


class IncidentEngine:

    def create_incident_from_alert(self, alert_data: dict) -> dict:
        inc_id = f"INC-{uuid4().hex[:8]}"
        return {
            "id": str(uuid4()),
            "incident_code": inc_id,
            "title": alert_data.get("message", "Alert Triggered"),
            "severity": alert_data.get("severity", "HIGH"),
            "status": "OPEN",
            "service": alert_data.get("service", "unknown-service"),
            "assigned_to": None,
            "started_at": datetime.now(timezone.utc),
            "resolved_at": None,
        }
