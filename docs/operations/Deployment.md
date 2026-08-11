# FACCP Operations & Deployment Guide

## Local Development Stack
Start the complete infrastructure with Docker Compose:
```bash
make dev-infra
make setup
make seed
```

## Running Production Kubernetes Stack
Apply the manifests to your Kubernetes cluster:
```bash
kubectl apply -f infrastructure/k8s/deployment.yaml
```

## Monitoring & Observability
- **Prometheus Metrics**: Scraped from `/metrics` endpoint across all services.
- **OTel Tracing**: OpenTelemetry spans exported to Jaeger collector.
- **Grafana Dashboard**: Pre-configured dashboards at `http://localhost:3000`.
