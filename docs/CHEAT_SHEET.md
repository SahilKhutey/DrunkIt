# 🚀 FACCP Platform Developer Cheat-Sheet

Quick-reference guide for running, testing, building, and operating the FACCP platform codebase.

---

## 🛠️ Service Port Allocations

| Service Name | Port | Description |
|---|---|---|
| **`faccp-gateway`** | `8000` | Unified Reverse Proxy, Rate Limiting & Service Router |
| **`faccp-identity`** | `8001` | OAuth2/OIDC, Argon2id, TOTP MFA, RBAC & JWT Rotation |
| **`faccp-consumer`** | `8002` | PII Vault with Field Encryption & GDPR/DPDP Consent |
| **`faccp-retailer`** | `8003` | Organization Onboarding, Store Geofencing & Licenses |
| **`faccp-catalog`** | `8004` | Master Product SKUs, Categories, Brands & Listings |
| **`faccp-inventory`** | `8005` | 15-Minute Stock Reservation Holds & Atomic Deductions |
| **`faccp-order`** | `8006` | Order State Machine Engine & Compliance Audit Pipeline |
| **`faccp-compliance`**| `8007` | Age, Hours, Dry-Day & Transaction Limit Engine |
| **`faccp-payment`** | `8008` | Intents, Double-Entry Financial Ledger & Refunds |
| **`faccp-delivery`** | `8009` | Dispatch Missions, GPS Location Tracking & Doorstep OTP |
| **`faccp-audit`** | `8010` | SHA256 Cryptographic Hash-Chained Tamper-Evident Ledger |
| **`faccp-risk`** | `8011` | Velocity & Anomaly Fraud Scoring Risk Engine |
| **`faccp-realtime`** | `8012` | WebSockets Live Order & Driver GPS Broadcast Gateway |
| **`faccp-analytics`** | `8013` | Time-Series Metric Aggregations & Compliance Reports |
| **`faccp-recommendation`**| `8014` | Product Discovery & CDP Affinity Matrix Scoring |
| **`faccp-whitelabel`**| `8015` | Multi-Tenant Branding Themes & Custom CNAME Router |
| **`faccp-support-agent`**| `8016` | Automated AI Support Agent & RAG Knowledge Search |

---

## 💻 Common Commands

### 1. Verification & Constitution Audit
```bash
# Run 46-step Constitution Audit
python scripts/constitution/check_compliance.py

# Run all unit tests
python -m pytest tests/unit/test_*.py

# Run E2E transaction flow test
python -m pytest tests/e2e/test_checkout_flow.py

# Run performance benchmark suite
python -m pytest tests/performance/test_load_benchmark.py
```

### 2. Infrastructure & Local Services
```bash
# Start Docker Infrastructure (Postgres, Redis, Kafka)
make dev-infra

# Run Database Migrations
make migrate

# Seed Initial Sample Data
make seed
```

### 3. Frontend Applications
```bash
# Start Consumer Web Portal (Port 3001)
pnpm --filter @faccp/consumer-web dev

# Start Admin Console (Port 3000)
pnpm --filter @faccp/admin-web dev

# Start Retailer Operations Console (Port 3002)
pnpm --filter @faccp/retailer-web dev

# Start Driver Mobile App (Port 3003)
pnpm --filter @faccp/driver-app dev
```
