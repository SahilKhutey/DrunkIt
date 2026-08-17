from services.security.app.models.enums import RiskDecision, RiskLevel


class RiskAggregator:

    def calculate(self, signals: list) -> tuple[float, RiskLevel]:
        score = sum(getattr(s, "score", s.get("score", 0.0)) for s in signals)
        score = min(score, 100.0)

        if score >= 80.0:
            level = RiskLevel.CRITICAL
        elif score >= 60.0:
            level = RiskLevel.HIGH
        elif score >= 30.0:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW

        return score, level


class SecurityDecisionEngine:

    def decide(self, score: float, level: RiskLevel) -> RiskDecision:
        if level == RiskLevel.LOW:
            return RiskDecision.ALLOW
        if level == RiskLevel.MEDIUM:
            return RiskDecision.MONITOR
        if level == RiskLevel.HIGH:
            return RiskDecision.HOLD
        if level == RiskLevel.CRITICAL:
            return RiskDecision.BLOCK
        return RiskDecision.REVIEW


class OrderSecurityGate:

    async def evaluate(self, compliance_result: dict, security_result: dict) -> dict:
        if compliance_result.get("decision") != "ALLOW":
            return {"decision": "DENY", "reason": "COMPLIANCE_DENIED"}

        sec_dec = security_result.get("decision")
        if sec_dec == "BLOCK" or sec_dec == RiskDecision.BLOCK:
            return {"decision": "BLOCK", "reason": "SECURITY_BLOCK"}

        if sec_dec in ("HOLD", "REVIEW", RiskDecision.HOLD, RiskDecision.REVIEW):
            return {"decision": "HOLD", "reason": "SECURITY_REVIEW"}

        return {"decision": "ALLOW", "reason": "ALL_CHECKS_PASSED"}


class RiskEngine:

    def __init__(self, repository=None, aggregator=None, decision_engine=None):
        self.repository = repository
        self.aggregator = aggregator or RiskAggregator()
        self.decision_engine = decision_engine or SecurityDecisionEngine()

    async def evaluate(self, subject_type: str, subject_id: str, signals: list | None = None) -> dict:
        recent_signals = signals or []
        if self.repository and not signals:
            recent_signals = await self.repository.get_recent(subject_type, subject_id)

        score, level = self.aggregator.calculate(recent_signals)
        decision = self.decision_engine.decide(score, level)

        return {
            "subject_type": subject_type,
            "subject_id": subject_id,
            "risk_score": score,
            "risk_level": level.value if hasattr(level, "value") else str(level),
            "decision": decision.value if hasattr(decision, "value") else str(decision),
            "signals": [getattr(s, "signal_type", s.get("signal_type")) for s in recent_signals],
        }
