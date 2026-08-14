# Runbook: High API Latency

## Symptoms
- Alert: `HTTPRequestsP95LatencyHigh`
- P95 HTTP latency > 500ms on API Gateway or Order Service.

## Diagnostic Steps
1. Inspect Grafana Service Health Dashboard: Check P95 and P99 latency panels.
2. Check OpenTelemetry Distributed Traces in Tempo/Jaeger: Find slow span in trace waterfall.
3. Check PostgreSQL Connection Pool & Slow Queries: Identify long-running SQL queries or missing indexes.

## Immediate Mitigation Actions
1. If DB connection pool is saturated, scale service replicas or increase DB pool size parameters.
2. Enable Redis caching for read-heavy routes.
