# Runbook: Kafka Consumer Lag High

## Symptoms
- Alert: `KafkaConsumerLagHigh`
- Increasing lag metrics on consumer group `faccp-consumer-group`.
- Order processing delay exceeding SLA threshold.

## Diagnostic Steps
1. Verify Kafka Broker Health: Check CPU, memory, disk I/O on Bitnami/Strimzi Kafka nodes.
2. Check Consumer Service Logs: `kubectl logs -l app=order-service --tail=200`.
3. Check Database Locks: Inspect PostgreSQL active queries to see if consumer DB commits are blocking on row locks (`FOR UPDATE`).
4. Inspect Poison Messages: Check if a malformed event is causing consumer retries or crash loops.

## Immediate Mitigation Actions
1. If consumer replica count is below partition count, scale up consumer instances:
   `kubectl scale deployment order-service --replicas=5`.
2. If poison message is identified, push to DLQ using admin CLI tool to allow partition consumption to unblock.
3. Restart failed consumer pods: `kubectl rollout restart deployment/order-service`.

## Post-Incident Actions
1. Add regression test for the unhandled event format.
2. Replay dead letter queue items after applying hotfix.
