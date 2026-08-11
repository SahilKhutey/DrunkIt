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
  AUDIT_CREATED = 'audit.created'
}

export interface DomainEvent<T> {
  eventId: string;
  topic: EventTopic;
  version: string;
  producer: string;
  timestamp: string;
  correlationId: string;
  payload: T;
}

export type ConsumerVerifiedEvent = DomainEvent<ZeroKnowledgeAgeProof>;
export type OrderCreatedEvent = DomainEvent<OrderDetails>;
export type LicenseUpdatedEvent = DomainEvent<ExciseLicense>;
export type AuditCreatedEvent = DomainEvent<AuditEvent>;
