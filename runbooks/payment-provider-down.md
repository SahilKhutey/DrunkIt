# Runbook: Payment Provider Outage

## Symptoms
- Alert: `PaymentProviderOutage` / `CircuitBreakerOpen`
- Circuit breaker state for Payment Service transitions to `OPEN`.
- High failure count on `POST /payments` and `POST /payments/{id}/capture`.

## Diagnostic Steps
1. Verify Payment Provider Webhook/API status page.
2. Check `ResilientClient` logs for timeout or 5xx responses from provider endpoints.
3. Check `event_outbox` table status for pending payment events.

## Immediate Mitigation Actions
1. Confirm circuit breaker is `OPEN` (preventing worker thread pool exhaustion).
2. Enable mock fallback provider for local/staging or switch to secondary payment gateway if available.
3. Queue incoming payment intents in `PAYMENT_PENDING` state until provider status restores to `HALF_OPEN` / `CLOSED`.

## Post-Incident Actions
1. Execute reconciliation service `ReconciliationService.reconcile()` to verify local DB payment statuses against provider records.
