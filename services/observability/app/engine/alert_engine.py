import hashlib
from typing import Any


def alert_fingerprint(code: str, service: str) -> str:
    raw = f"{code}:{service}"
    return hashlib.sha256(raw.encode()).hexdigest()


class AlertEngine:

    def evaluate(self, metric_value: float, threshold: float, operator: str) -> bool:
        if operator == "greater_than":
            return metric_value > threshold
        if operator == "less_than":
            return metric_value < threshold
        if operator == "equals":
            return metric_value == threshold
        raise ValueError(f"Unsupported operator: {operator}")
