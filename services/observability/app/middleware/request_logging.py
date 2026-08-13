import json
from datetime import datetime, timezone

SENSITIVE_FIELDS = {
    "password",
    "token",
    "authorization",
    "secret",
    "api_key",
    "cvv",
    "card_number",
}


def redact(payload: dict) -> dict:
    result = {}
    for key, value in payload.items():
        if key.lower() in SENSITIVE_FIELDS:
            result[key] = "[REDACTED]"
        elif isinstance(value, dict):
            result[key] = redact(value)
        else:
            result[key] = value
    return result


class StructuredLogger:

    def __init__(self, service: str):
        self.service = service

    def _log(self, level: str, event: str, **fields):
        clean_fields = redact(fields)
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "service": self.service,
            "event": event,
            **clean_fields,
        }
        print(json.dumps(record))
        return record

    def info(self, event: str, **fields):
        return self._log("INFO", event, **fields)

    def error(self, event: str, **fields):
        return self._log("ERROR", event, **fields)

    def warning(self, event: str, **fields):
        return self._log("WARNING", event, **fields)
