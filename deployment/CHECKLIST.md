# DrunkIt Production Go-Live Checklist

## 1. Quality Gates
- [x] Code linting & static analysis passing
- [x] Unit tests passing (300+ tests)
- [x] OpenAPI specifications validated
- [x] JSON event envelope & payload schemas validated
- [x] Database ownership isolation boundaries verified

## 2. Infrastructure & Security
- [x] Multi-stage non-root container images built (`USER drunkit`)
- [x] Kubernetes manifests configured with `securityContext` (`runAsNonRoot: true`, dropped capabilities)
- [x] PodDisruptionBudgets and HorizontalPodAutoscalers active
- [x] Secrets scanning verified (no committed production keys or passwords)
- [x] Production configuration rules enforced (`validate_production_config`)

## 3. Operations & Disaster Recovery
- [x] Alembic database migrations verified against single head
- [x] PostgreSQL backup and restore procedure tested (`test_restore.py`)
- [x] Automated rollback script verified (`rollback.sh`)
- [x] Health check probes verified (`/health/live` & `/health/ready`)
- [x] End-to-end multi-service business lifecycle tested
