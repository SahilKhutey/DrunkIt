# Multi-Region High Availability & Disaster Recovery Runbook

**Severity:** SEV1 (Primary Region Down)  
**RTO Target:** < 15 minutes  
**RPO Target:** < 1 minute  
**Primary Region:** `ap-south-1` (Mumbai)  
**Secondary DR Region:** `ap-south-2` (Hyderabad)  

---

## 1. Overview & Failure Triggers

This runbook covers catastrophic failure of the primary AWS region (`ap-south-1`), including complete loss of EKS control plane, RDS master, or AWS backbone network.

### Automated Alerts Triggering Failover Assessment:
- Route 53 Health Check Status: `HEALTHY -> UNHEALTHY` for > 3 consecutive probes.
- API Gateway Global Edge Error Rate > 50% for > 3 minutes.
- Aurora Global Database replication lag alert.

---

## 2. Step-by-Step Disaster Recovery Failover Procedure

### Step 1: Confirm Primary Region Loss (2 Minutes)
Run the automated DR verification script:
```bash
python scripts/dr/verify_dr_failover.py
```

### Step 2: Promote Secondary RDS Aurora DB (3 Minutes)
Promote the read replica in `ap-south-2` to standalone write master:
```bash
aws rds failover-global-cluster \
    --global-cluster-identifier faccp-global-db \
    --target-db-cluster-identifier arn:aws:rds:ap-south-2:123456789012:cluster:faccp-db-secondary
```

### Step 3: Switch Route 53 DNS Traffic (2 Minutes)
Update Route 53 DNS records to point `api.faccp.com` to `ap-south-2` Network Load Balancer:
```bash
aws route53 change-resource-record-sets \
    --hosted-zone-id Z1234567890 \
    --change-batch file://infrastructure/dr/route53_failover.json
```

### Step 4: Verify ArgoCD GitOps Sync in Secondary Cluster (3 Minutes)
```bash
argocd app sync faccp-platform-secondary --prune
```

### Step 5: Validate Audit & Ledger Integrity (2 Minutes)
Run the master constitution compliance script in the failover region:
```bash
python scripts/constitution/check_compliance.py
```
