import { AuditEvent, OrderDetails, ZeroKnowledgeAgeProof, ExciseLicense } from '@faccp/shared-types';

export enum EventTopic {
  CONSUMER_CREATED = 'consumer.created',
  CONSUMER_VERIFIED = 'consumer.verified',
  SELLER_CREATED = 'seller.created',
  LICENSE_UPDATED = 'license.updated',
  INVENTORY_UPDATED = 'inventory.updated',
  ORDER_CREATED = 'order.created',
  ORDER_CONFIRMED = 'order.confirmed',
  ORDER_CANCELLED = 'order.cancelled',
  VERIFICATION_COMPLETED = 'verification.completed',
  COMPLIANCE_VIOLATION = 'compliance.violation',
  AUDIT_CREATED = 'audit.created',
}

/**
 * Canonical FACCP event envelope.
 *
 * Every domain event published to Kafka MUST conform to this shape.
 * Fields enable:
 *   - Idempotency: eventId (deduplicate on consumer side)
 *   - Tracing: correlationId (request trace), causationId (parent event)
 *   - Optimistic concurrency: aggregateId + aggregateVersion
 *   - Schema evolution: schemaVersion
 *
 * @see packages/sdk-python/faccp_sdk/events/envelope.py (Python counterpart)
 */
export interface DomainEvent<T> {
  /** UUID v4 — unique per event instance. Use for consumer-side deduplication. */
  eventId: string;

  /** Fully-qualified topic name from EventTopic enum. */
  topic: EventTopic;

  /** Schema version string e.g. "1.0". Increment on breaking payload changes. */
  schemaVersion: string;

  /** Publishing service identifier e.g. "order-service". */
  producer: string;

  /** ISO-8601 UTC timestamp when the event occurred in the domain. */
  occurredAt: string;

  /**
   * Correlation ID — propagated from the originating HTTP request.
   * Ties together all events produced by a single user request across services.
   */
  correlationId: string;

  /**
   * Causation ID — the eventId of the event (or request ID) that directly
   * caused this event to be emitted. Forms a causal chain for event replay.
   */
  causationId: string;

  /** The domain aggregate this event belongs to e.g. an order UUID. */
  aggregateId: string;

  /** Monotonic version of the aggregate at the time this event was emitted. */
  aggregateVersion: number;

  /** Domain-specific event payload. */
  payload: T;
}

// ─── Typed event aliases ──────────────────────────────────────────────────────

export type ConsumerVerifiedEvent = DomainEvent<ZeroKnowledgeAgeProof>;
export type OrderCreatedEvent = DomainEvent<OrderDetails>;
export type LicenseUpdatedEvent = DomainEvent<ExciseLicense>;
export type AuditCreatedEvent = DomainEvent<AuditEvent>;
