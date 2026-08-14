# Runbook: Order Saga Stuck

## Symptoms
- Alert: `SagaStuckInPendingState`
- `SagaInstance` state remains in `PAYMENT_PENDING`, `INVENTORY_PENDING`, or `FULFILLMENT_PENDING` > 5 minutes.

## Diagnostic Steps
1. Query `saga_instances` table for stalled order ID: `SELECT * FROM saga_instances WHERE order_id = '...';`.
2. Inspect `event_outbox` for un-published events tied to `aggregate_id = order_id`.
3. Check consumer logs for unhandled exceptions during saga step execution.

## Immediate Mitigation Actions
1. If event was missed in outbox, trigger `OutboxWorker.publish_batch()`.
2. If saga compensation is required, manually trigger compensation via `OrderSaga.on_inventory_failed()`.

## Post-Incident Actions
1. Add saga step timeout worker to automatically transition stuck sagas to `COMPENSATING` after SLA expiration.
