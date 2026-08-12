# FACCP Delivery System & Delivery Engine Architecture

## Executive Overview
The Delivery System is an independent fulfilment & logistics platform subsystem. It converts an accepted order into a legally permitted, operationally feasible, and real-time trackable delivery mission.

```
                           DELIVERY PLATFORM
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
   ORDER SERVICE              STORE SERVICE             USER SERVICE
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  ▼
                       DELIVERY ORCHESTRATOR
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        ▼                         ▼                         ▼
 Fulfilment Engine          Dispatch Engine           Verification
        │                         │                         │
        ▼                         ▼                         ▼
 Store Selection             Driver Pool             Handoff Rules
        │                         │                         │
        └─────────────────────────┼─────────────────────────┘
                                  ▼
                            Route Engine
                                  │
                                  ▼
                          Delivery Job Manager
                                  │
             ┌────────────────────┼────────────────────┐
             ▼                    ▼                    ▼
        Driver App           Tracking Engine       Notifications
             │                    │                    │
             └────────────────────┼────────────────────┘
                                  ▼
                          Delivery Completion
                                  │
                         ┌────────┴────────┐
                         ▼                 ▼
                    Proof of Delivery   Audit
```

---

## 🔄 Delivery Lifecycle State Machine (14 States)

```text
REQUESTED → PLANNING → DISPATCHING → ASSIGNED → PICKUP_READY → PICKED_UP → IN_TRANSIT → ARRIVING → HANDOFF_CHECK → DELIVERED
```
*Failure Paths*: `CANCELLED`, `FAILED`, `RETURN_REQUIRED`, `RETURNED`.

---

## 🚗 Driver States (9 States)
`OFFLINE`, `AVAILABLE`, `RESERVED`, `ASSIGNED`, `PICKING_UP`, `DELIVERING`, `PAUSED`, `OFFLINE_PENDING`, `SUSPENDED`.

---

## 🛡️ 3-Point Controlled Verification & Handoff
1. **Order / Account Verification**: Initial identity check at checkout.
2. **Store $\rightarrow$ Driver Verification**: Physical package check & store pickup verification.
3. **Driver $\rightarrow$ Customer Verification**: Controlled handoff verification (Age / Identity / QR OTP / Digital Signature) resulting in **Proof of Delivery (POD)**.

---

## 📦 20 Core Service Modules

1. `order-adapter`: Consumes order events.
2. `fulfilment`: Store selection & store load balancing.
3. `delivery-orchestrator`: Main workflow state machine controller.
4. `dispatch`: Driver assignment & scoring engine.
5. `driver`: Driver profile & status management.
6. `fleet`: Fleet management & vehicle capacity.
7. `routing`: Route calculation & traffic adapters.
8. `tracking`: Real-time GPS stream processor.
9. `eta`: Dynamic multi-segment ETA calculation engine.
10. `verification`: Handoff verification logic.
11. `handoff`: Package handoff rules & token checks.
12. `delivery-zone`: Serviceability geofences & polygon bounds.
13. `serviceability`: Real-time delivery availability checker.
14. `notifications`: Real-time push & SMS notifications adapter.
15. `cancellation`: State-aware cancellation rules engine.
16. `returns`: Reverse logistics & store return workflows.
17. `proof-of-delivery`: POD evidence capture & audit signer.
18. `incident`: Delivery failure & exception handler.
19. `pricing`: Delivery fee & surcharge calculator adapter.
20. `analytics`: Telemetry & performance metrics emitter.

---

## 📡 14 Coherent Event Topics

- `delivery.requested`
- `delivery.planned`
- `delivery.assigned`
- `delivery.pickup.ready`
- `delivery.picked_up`
- `delivery.location.updated`
- `delivery.eta.updated`
- `delivery.arriving`
- `delivery.verification.required`
- `delivery.completed`
- `delivery.failed`
- `delivery.cancelled`
- `delivery.return.required`
- `delivery.incident.opened`

---

## 📅 10-Phase Development Roadmap

- **D1**: Delivery Domain (Entities, state machine, lifecycle).
- **D2**: Fulfilment (Store selection, serviceability, inventory check).
- **D3**: Dispatch Engine (Driver pool, candidate filtering, scoring algorithm).
- **D4**: Driver System (Driver app backend, online/offline, job management).
- **D5**: Tracking Engine (GPS gateway, Redis stream, WebSocket broadcast).
- **D6**: ETA & Routing (Maps API adapters, dynamic travel time calculation).
- **D7**: Controlled Verification & Handoff (Handoff tokens, POD capture, audit emission).
- **D8**: Failure & Incident Recovery (Cancellations, return flow, incident management).
- **D9**: Operations & Dashboards (Admin control center, retailer interface, driver app).
- **D10**: ML Optimization (Dynamic batching, ML driver assignment, demand prediction).
