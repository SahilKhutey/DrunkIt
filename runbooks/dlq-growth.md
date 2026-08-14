# Runbook: Dead Letter Queue (DLQ) Growth

## Symptoms
- Alert: `DLQEventsTotalSpike`
- Count of events in topic `faccp.events.dlq` > 0.

## Diagnostic Steps
1. Inspect DLQ Event Payload: `python scripts/inspect_dlq.py --topic faccp.events.dlq`.
2. Review failure context metadata: `original_topic`, `error`, `attempts`, `failed_at`.
3. Check code release history to determine if recent schema migration introduced non-backwards-compatible schema attributes.

## Immediate Mitigation Actions
1. Fix schema definition or serialization bug in consumer code.
2. Deploy fix to microservices.
3. Trigger DLQ replay script: `python scripts/replay_dlq.py --topic faccp.events.dlq`.

## Post-Incident Actions
1. Audit schema compatibility test suite.
