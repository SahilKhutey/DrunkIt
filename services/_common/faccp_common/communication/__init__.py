"""Communication system — Kafka client, event envelope, retry, circuit breaker."""

from faccp_common.communication.envelope import (
    EventEnvelope,
    StandardEvent,
    EventMetadata,
    create_envelope,
    parse_envelope,
)
from faccp_common.communication.producer import EventProducer
from faccp_common.communication.consumer import EventConsumer, EventHandler, IdempotentConsumer
from faccp_common.communication.topics import TopicRegistry

from faccp_common.communication.reliability import (
    RetryPolicy,
    CircuitBreaker,
    with_retry,
    with_circuit_breaker,
)
from faccp_common.communication.request_envelope import (
    StandardRequest,
    CorrelationContext,
    ServicePermissionMatrix,
)


__all__ = [
    "EventEnvelope",
    "StandardEvent",
    "EventMetadata",
    "create_envelope",
    "parse_envelope",
    "EventProducer",
    "EventConsumer",
    "EventHandler",
    "IdempotentConsumer",
    "TopicRegistry",

    "RetryPolicy",
    "CircuitBreaker",
    "with_retry",
    "with_circuit_breaker",
    "StandardRequest",
    "CorrelationContext",
    "ServicePermissionMatrix",
]


