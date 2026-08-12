# FACCP Communication System Architecture

## Executive Overview
The Communication System is the controlled nervous system connecting all independent domains. It carries trust, authorization, state, events, failures, and accountability between independent services.

```
                    COMMUNICATION SYSTEM
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    Synchronous       Asynchronous       External
    Communication     Communication       Communication
          │                │                │
       REST/gRPC       Event Bus          APIs
       WebSocket       Kafka             Providers
       GraphQL         Queues            Partners
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                 Communication Control
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
       Security         Reliability      Observability
```

---

## 📊 The 5 Communication Layers

1. **Layer 1: Client Communication (L1)**: Entry point for external clients via HTTPS (TLS 1.3), REST, WebSocket (real-time tracking), and SSE through API Gateway.
2. **Layer 2: Synchronous Service Communication (L2)**: Service-to-service RPC via HTTP/REST or gRPC for immediate answers (Eligibility, Inventory Check, Pricing).
3. **Layer 3: Asynchronous Communication (L3)**: Event-driven decoupled integration via Apache Kafka (`order.events`, `payment.events`, `compliance.events`).
4. **Layer 4: Real-Time Communication (L4)**: Live delivery tracking and driver location updates via WebSocket through Realtime Gateway.
5. **Layer 5: External Communication (L5)**: Third-party integration boundary (Razorpay, Onfido, Mapbox, Twilio) using vendor-agnostic adapter interfaces.

---

## 🔒 Communication Security & Permission Control

### Service Identity
Every service possesses a unique, verified service identity token (`ServiceIdentity`) issued via short-lived JWTs (5-minute TTL).

### Service Permission Matrix (`ServicePermissionMatrix`)
Strict caller-to-target action control:
- `checkout-service` → `inventory-service` (`reserve`, `release`)
- `checkout-service` → `compliance-service` (`evaluate`)
- `checkout-service` → `payment-service` (`create_intent`)
- `consumer-service` → `payment-service` (EXPLICIT DENIAL: NO direct access)

---

## 📦 Envelopes & Correlation Standards

### Standard Internal Request Envelope (`StandardRequest`)
```json
{
  "request_id": "req_abc123",
  "correlation_id": "corr_xyz789",
  "timestamp": "2026-08-12T12:00:00Z",
  "source": "checkout-service",
  "actor": {
    "type": "consumer",
    "id": "usr_consumer123"
  },
  "payload": {}
}
```

### Standard Event Envelope (`StandardEvent`)
```json
{
  "event_id": "evt_abc123def456",
  "event_type": "order.created",
  "version": 1,
  "producer": "order-service",
  "timestamp": "2026-08-12T12:00:00Z",
  "correlation_id": "corr_xyz789",
  "causation_id": "evt_previous_event",
  "payload": {}
}
```

---

## ⚡ Reliability & Error Handling

- **Exponential Backoff with Jitter (`RetryPolicy`)**: Max 4 attempts with randomized jitter to prevent thundering herd.
- **Idempotent Consumption (`IdempotencyConsumer`)**: Event deduplication keyed on unique `event_id`.
- **Dead-Letter Queue (DLQ)**: Preserves failed message context (`DLQRecord`) after retries are exhausted.
- **Circuit Breaker (`CircuitBreaker`)**: 3-state protection (`CLOSED`, `OPEN`, `HALF_OPEN`) for external providers.
