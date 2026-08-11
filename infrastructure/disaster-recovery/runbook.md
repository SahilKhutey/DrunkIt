# FACCP Disaster Recovery Runbook

## Recovery Time Objectives (RTO) & Recovery Point Objectives (RPO)

| Tier | Service | RTO | RPO | Strategy |
|---|---|---|---|---|
| Tier 1 (Critical) | order, payment, compliance, audit | 15 min | 5 min | Hot standby, multi-AZ |
| Tier 2 (Important) | identity, consumer, retailer, catalog | 1 hour | 15 min | Warm standby, daily snapshot |
| Tier 3 (Standard) | inventory, risk, delivery, notification | 4 hours | 1 hour | Cold standby, weekly backup |
| Tier 4 (Archive) | analytics, reporting | 24 hours | 24 hours | Daily backup only |

## Backup Schedule
- **Full backup**: Daily at 02:00 UTC
- **Incremental (WAL)**: Every 15 minutes
- **Audit chain snapshot**: Every 6 hours
- **Object storage**: Real-time replication
- **Retention**: 30 days hot, 1 year cold

## Disaster Scenarios

### Scenario 1: Single Service Failure
**Detection**: Health check fails, alerting triggers
**Response**:
1. Kubernetes auto-restarts pod
2. If persistent, check logs
3. If database, check connection pool
4. Escalate to on-call if not resolved in 15 min

### Scenario 2: Database Corruption
**Detection**: Query errors, integrity check fails
**Response**:
1. Stop affected service
2. Identify last known good backup
3. Restore to new database instance
4. Replay WAL to recovery point
5. Verify audit chain integrity
6. Resume service

### Scenario 3: Region Failure
**Detection**: All services in region unreachable
**Response**:
1. Failover to secondary region (DNS update)
2. Promote read replicas to primary
3. Restore from cross-region backup
4. Verify data consistency
5. Communicate to stakeholders

### Scenario 4: Audit Chain Tampering Detected
**Detection**: `audit_chain_broken_events > 0` alert
**Response**:
1. **DO NOT** continue normal operations
2. Quarantine affected service
3. Preserve current state for forensic analysis
4. Notify DPO and Security Admin
5. Initiate incident response procedure
6. Restore from last known good audit chain
7. Document incident in compliance log

### Scenario 5: Data Breach
**Detection**: Unusual data access patterns
**Response**:
1. Activate incident response team
2. Identify scope of breach
3. Preserve evidence
4. Notify DPO within 72 hours (GDPR)
5. Notify affected users
6. Reset all credentials
7. Review and patch vulnerability
8. Document in compliance log

## Backup Verification
Run weekly:
```bash
./restore.sh $(ls -t /backups/faccp_backup_*.tar.gz.enc | head -1) faccp_test
```
