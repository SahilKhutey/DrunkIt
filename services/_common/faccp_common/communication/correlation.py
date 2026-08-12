"""
Correlation Context & Tracing Headers.
"""

from __future__ import annotations

import uuid
from typing import Any


class CorrelationContext:
    def __init__(self, correlation_id: str | None = None, causation_id: str | None = None) -> None:
        self.correlation_id = correlation_id or f"corr_{uuid.uuid4().hex[:16]}"
        self.causation_id = causation_id

    def child(self) -> CorrelationContext:
        return CorrelationContext(
            correlation_id=self.correlation_id,
            causation_id=f"req_{uuid.uuid4().hex[:16]}",
        )

    def to_headers(self) -> dict[str, str]:
        return {
            "X-Correlation-ID": self.correlation_id,
            "X-Causation-ID": self.causation_id or "",
        }
