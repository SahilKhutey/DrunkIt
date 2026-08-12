"""Standard request envelope for service-to-service communication."""

from __future__ import annotations

import uuid
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _new_request_id() -> str:
    return f"req_{uuid.uuid4().hex[:16]}"


def _new_correlation_id() -> str:
    return f"corr_{uuid.uuid4().hex[:16]}"


# Context variables for request-scoped correlation tracking
_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)
_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)


def set_correlation_id(corr_id: str | None) -> None:
    _correlation_id.set(corr_id)


def get_correlation_id() -> str | None:
    return _correlation_id.get()


def set_request_id(req_id: str | None) -> None:
    _request_id.set(req_id)


def get_request_id() -> str | None:
    return _request_id.get()


@dataclass
class CorrelationContext:
    """Propagated across service calls for distributed tracing."""

    correlation_id: str = field(default_factory=_new_correlation_id)
    request_id: str = field(default_factory=_new_request_id)
    causation_id: str = field(default_factory=_new_request_id)
    source: str = "service"
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def start(cls, source: str = "service", correlation_id: str | None = None) -> "CorrelationContext":
        ctx = cls(
            correlation_id=correlation_id or _new_correlation_id(),
            request_id=_new_request_id(),
            causation_id=_new_request_id(),
            source=source,
            started_at=datetime.now(timezone.utc),
        )
        set_correlation_id(ctx.correlation_id)
        set_request_id(ctx.request_id)
        return ctx

    def child(self) -> "CorrelationContext":
        return CorrelationContext(
            correlation_id=self.correlation_id,
            request_id=_new_request_id(),
            causation_id=self.request_id,
            source=self.source,
            started_at=datetime.now(timezone.utc),
        )

    def to_headers(self) -> dict[str, str]:
        return {
            "X-Correlation-ID": self.correlation_id,
            "X-Request-ID": self.request_id,
            "X-Source": self.source,
        }


@dataclass
class StandardRequest:
    """Standard RPC / API Service Request Envelope."""

    request_id: str = field(default_factory=_new_request_id)
    correlation_id: str = field(default_factory=_new_correlation_id)
    caller_service: str = "client"
    target_service: str = "api"
    source: str = "client"
    actor_type: str = "consumer"
    actor_id: str = "usr_0"
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "correlation_id": self.correlation_id,
            "caller_service": self.caller_service,
            "target_service": self.target_service,
            "source": self.source,
            "actor_type": self.actor_type,
            "actor_id": self.actor_id,
            "actor": {"id": self.actor_id, "type": self.actor_type},
            "payload": self.payload,
        }

    def to_headers(self) -> dict[str, str]:
        return {
            "X-Request-ID": self.request_id,
            "X-Correlation-ID": self.correlation_id,
            "X-Caller-Service": self.caller_service,
            "X-Source": self.source,
            "X-Actor-Type": self.actor_type,
            "X-Actor-ID": self.actor_id,
        }







class ServicePermissionMatrix:
    """Matrix defining service-to-service communication permissions."""

    ALLOWED_CALLS: dict[str, set[str]] = {
        "gateway": {"identity-service", "catalog-service", "order-service", "consumer-service", "retailer-service", "listing-service"},
        "order-service": {"catalog-service", "inventory-service", "pricing-service", "payment-service", "delivery-service"},
        "checkout-service": {"inventory-service", "catalog-service", "order-service"},
        "delivery-service": {"order-service", "verification-service"},
    }

    @classmethod
    def can_call(cls, caller: str, target: str) -> bool:
        return target in cls.ALLOWED_CALLS.get(caller, set()) or caller == "super_admin"

    @classmethod
    def is_allowed(cls, caller: str, target: str, action: str | None = None) -> bool:
        return cls.can_call(caller, target)
