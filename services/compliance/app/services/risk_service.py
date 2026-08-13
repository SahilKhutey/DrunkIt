from datetime import datetime, timezone
from uuid import uuid4

from services.compliance.app.engine.risk_engine import RiskEngine


class RiskService:

    def __init__(self, risk_engine: RiskEngine | None = None):
        self.risk_engine = risk_engine or RiskEngine()
        self.signals: dict[str, list[dict]] = {}

    async def record_signal(
        self,
        subject_type: str,
        subject_id: str,
        signal_type: str,
        severity: str,
        score: float,
        metadata: dict | None = None,
    ) -> dict:

        record = {
            "id": str(uuid4()),
            "subject_type": subject_type,
            "subject_id": subject_id,
            "signal_type": signal_type,
            "severity": severity,
            "score": score,
            "metadata_json": metadata or {},
            "created_at": datetime.now(timezone.utc),
        }
        self.signals.setdefault(subject_id, []).append(record)
        return record

    async def evaluate_risk(self, subject_id: str) -> dict:
        subject_signals = self.signals.get(subject_id, [])
        return self.risk_engine.calculate(subject_signals)
