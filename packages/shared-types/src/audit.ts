export interface AuditEvent {
  sequenceNumber: number;
  eventId: string;
  eventType: string;
  actorId: string;
  actorType: 'CONSUMER' | 'RETAILER_STAFF' | 'DELIVERY_AGENT' | 'PLATFORM_ADMIN' | 'SYSTEM';
  action: string;
  resourceId: string;
  resourceType: string;
  jurisdiction: string;
  policyVersion?: string;
  payloadHash: string;
  prevHash: string;
  currentHash: string;
  timestamp: string;
}

export interface AuditChainIntegrityReport {
  totalEvents: number;
  validChain: boolean;
  tamperedIndex?: number;
  lastHash: string;
  verifiedAt: string;
}
