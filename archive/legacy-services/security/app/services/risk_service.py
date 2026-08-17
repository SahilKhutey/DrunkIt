from datetime import datetime, timezone
from uuid import uuid4

from services.security.app.engine.risk_engine import RiskEngine


class RiskService:

    def __init__(self, risk_engine: RiskEngine | None = None):
        self.risk_engine = risk_engine or RiskEngine()
        self.signals: dict[str, list[dict]] = {}

    async def add_signal(
        self,
        subject_type: str,
        subject_id: str,
        signal_type: str,
        score: float,
        severity: str = "MEDIUM",
        source: str = "SYSTEM",
    ) -> dict:

        sig = {
            "id": str(uuid4()),
            "subject_type": subject_type,
            "subject_id": subject_id,
            "signal_type": signal_type,
            "severity": severity,
            "score": score,
            "source": source,
            "created_at": datetime.now(timezone.utc),
        }
        self.signals.setdefault(subject_id, []).append(sig)
        return sig

    async def evaluate(self, subject_type: str, subject_id: str, operation: str = "GENERAL") -> dict:
        subject_signals = self.signals.get(subject_id, [])
        return await self.risk_engine.evaluate(subject_type, subject_id, signals=subject_signals)

    async def get_signals(self, subject_type: str, subject_id: str) -> list[dict]:
        return self.signals.get(subject_id, [])
