from datetime import datetime, timezone
from uuid import uuid4


class TraceService:

    def __init__(self):
        self.spans: list[dict] = []

    def start_span(self, trace_id: str, name: str, service: str) -> dict:
        span_id = str(uuid4())
        span = {
            "trace_id": trace_id,
            "span_id": span_id,
            "name": name,
            "service": service,
            "started_at": datetime.now(timezone.utc),
            "duration_ms": 0.0,
            "status": "OK",
        }
        self.spans.append(span)
        return span

    def finish_span(self, span_id: str, duration_ms: float, status: str = "OK"):
        for s in self.spans:
            if s["span_id"] == span_id:
                s["duration_ms"] = duration_ms
                s["status"] = status
                break
