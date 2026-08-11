# FACCP System Architecture

## Overview
The Federated Alcohol Commerce & Compliance Platform (FACCP) is built as a multi-domain, zero-trust microservice platform. Every domain service manages its own isolated PostgreSQL database and communicates via HTTP REST APIs and asynchronous Kafka event streaming.

```
                  ┌──────────────────────┐
                  │     API Gateway      │ (Port 8000)
                  └──────────┬───────────┘
                             │
     ┌───────────────────────┼───────────────────────┐
     ▼                       ▼                       ▼
┌──────────────┐    ┌─────────────────┐    ┌──────────────────┐
│ Identity Svc │    │ Compliance Svc  │    │    Order Svc     │
│  (Port 8001) │    │   (Port 8007)   │    │   (Port 8006)    │
└──────────────┘    └─────────────────┘    └─────────┬────────┘
                                                     │
                                                     ▼
                                           ┌──────────────────┐
                                           │    Audit Svc     │
                                           │   (Port 8008)    │
                                           │ (Merkle-Chained) │
                                           └──────────────────┘
```

## Microservices Domain Matrix
- **Identity Service**: OAuth2 JWT issuer, Argon2id/bcrypt auth, TOTP MFA, RBAC permissions.
- **Consumer Service**: Privacy-by-design identity vault, encrypted PII, ZK-age claims.
- **Retailer Service**: Organization onboarding, store locations, state excise license management.
- **Catalog Service**: Product SKUs, ABV taxonomy, brand pricing, catalog search.
- **Inventory Service**: Stock reservation locks, TTL expiration, batch tracking.
- **Order Service**: Finite state machine transitions, async compliance & inventory pipeline.
- **Compliance Service**: Pure-Python rule evaluation, dry days calendar, versioned policies.
- **Audit Service**: SHA-256 Merkle hash-chained immutable audit log with sequence verification.
- **Risk Service**: Automated risk scoring & fraud detection engine.
- **Verification Service**: KYC document verification & age proofs.
- **Delivery Service**: Driver dispatch tasks & OTP handover verification.
- **Notification Service**: Multi-channel notification dispatch (SMS, Email, Push).

## Core Security & Compliance Guarantees
1. **PII Vault Isolation**: Sensitive personal identifiable information (name, DOB, full address) is encrypted with AES-256 Fernet in `faccp_consumer` database.
2. **Merkle Hash-Chaining**: Every audit event computes `event_hash = SHA256(previous_hash + payload)` ensuring tamper-evident history.
3. **Data-Driven Rules**: State compliance rules are defined as versioned YAML policies executed in-memory.
