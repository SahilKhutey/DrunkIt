from datetime import datetime, timezone
from uuid import uuid4

from services.observability.app.engine.alert_engine import AlertEngine, alert_fingerprint


class AlertService:

    def __init__(self, alert_engine: AlertEngine | None = None):
        self.alert_engine = alert_engine or AlertEngine()
        self.alerts_by_fingerprint: dict[str, dict] = {}
        self.alerts: dict[str, dict] = {}

    async def create_alert(
        self,
        code: str,
        service: str,
        severity: str = "HIGH",
        message: str = "",
        metadata_json: dict | None = None,
    ) -> dict:

        fp = alert_fingerprint(code, service)
        if fp in self.alerts_by_fingerprint:
            # Deduplicated! Return existing active alert
            existing = self.alerts_by_fingerprint[fp]
            existing["count"] = existing.get("count", 1) + 1
            return existing

        alert_id = str(uuid4())
        record = {
            "id": alert_id,
            "alert_code": code,
            "service": service,
            "severity": severity,
            "status": "ACTIVE",
            "message": message or f"Alert triggered: {code} for {service}",
            "fingerprint": fp,
            "count": 1,
            "metadata_json": metadata_json or {},
            "created_at": datetime.now(timezone.utc),
        }
        self.alerts_by_fingerprint[fp] = record
        self.alerts[alert_id] = record
        return record

    async def get_active_alerts(self) -> list[dict]:
        return [a for a in self.alerts.values() if a["status"] == "ACTIVE"]
