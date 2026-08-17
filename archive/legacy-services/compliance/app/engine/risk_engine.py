class RiskEngine:

    def calculate(self, signals: list) -> dict:
        score = 0.0
        for sig in signals:
            score += getattr(sig, "score", sig.get("score", 0.0))

        if score >= 80.0:
            level = "HIGH"
        elif score >= 40.0:
            level = "MEDIUM"
        else:
            level = "LOW"

        return {
            "score": score,
            "level": level,
        }
