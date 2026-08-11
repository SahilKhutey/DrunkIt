import hashlib
import json
import time
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from .models import AuditEventCreate, AuditEventRecord, AuditChainIntegrityReport

app = FastAPI(
    title="FACCP Cryptographic Hash-Chained Audit Service",
    description="Non-Repudiable Merkle-Chained Regulatory Event Logger & Governance Inspector Engine",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

AUDIT_LOG_STORE: List[AuditEventRecord] = []

def _compute_event_hash(seq: int, event_id: str, actor_id: str, action: str, resource_id: str, payload_hash: str, prev_hash: str, timestamp: str) -> str:
    raw_str = f"{seq}:{event_id}:{actor_id}:{action}:{resource_id}:{payload_hash}:{prev_hash}:{timestamp}"
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

# Seed Genesis Audit Event
seed_timestamp = str(int(time.time()) - 3600)
seed_payload_hash = hashlib.sha256(b"genesis_payload").hexdigest()
seed_event_id = "AUD-GENESIS-001"
seed_current_hash = _compute_event_hash(1, seed_event_id, "ADM-2001", "VERIFY_EXCISE_LICENSE", "LIC-KA-2026-9912", seed_payload_hash, GENESIS_HASH, seed_timestamp)

AUDIT_LOG_STORE.append(
    AuditEventRecord(
        sequence_number=1,
        event_id=seed_event_id,
        event_type="LICENSE_VERIFICATION",
        actor_id="ADM-2001",
        actor_type="PLATFORM_ADMIN",
        action="VERIFY_EXCISE_LICENSE",
        resource_id="LIC-KA-2026-9912",
        resource_type="EXCISE_LICENSE",
        jurisdiction="IN-KA",
        policy_version="1.0",
        payload_hash=seed_payload_hash,
        prev_hash=GENESIS_HASH,
        current_hash=seed_current_hash,
        timestamp=seed_timestamp
    )
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "audit-service", "chain_length": len(AUDIT_LOG_STORE)}

@app.post("/api/v1/audit/events", response_model=AuditEventRecord)
def record_event(req: AuditEventCreate):
    seq = len(AUDIT_LOG_STORE) + 1
    event_id = f"AUD-{uuid.uuid4().hex[:8].upper()}"
    raw_payload_str = json.dumps(req.payload, sort_keys=True)
    payload_hash = hashlib.sha256(raw_payload_str.encode("utf-8")).hexdigest()
    timestamp = str(int(time.time()))

    prev_hash = AUDIT_LOG_STORE[-1].current_hash if len(AUDIT_LOG_STORE) > 0 else GENESIS_HASH
    current_hash = _compute_event_hash(seq, event_id, req.actor_id, req.action, req.resource_id, payload_hash, prev_hash, timestamp)

    record = AuditEventRecord(
        sequence_number=seq,
        event_id=event_id,
        event_type=req.event_type,
        actor_id=req.actor_id,
        actor_type=req.actor_type,
        action=req.action,
        resource_id=req.resource_id,
        resource_type=req.resource_type,
        jurisdiction=req.jurisdiction,
        policy_version=req.policy_version,
        payload_hash=payload_hash,
        prev_hash=prev_hash,
        current_hash=current_hash,
        timestamp=timestamp
    )

    AUDIT_LOG_STORE.append(record)
    return record

@app.get("/api/v1/audit/events", response_model=List[AuditEventRecord])
def search_events(jurisdiction: str = None, actor_id: str = None):
    res = list(AUDIT_LOG_STORE)
    if jurisdiction:
        res = [e for e in res if e.jurisdiction == jurisdiction]
    if actor_id:
        res = [e for e in res if e.actor_id == actor_id]
    return res

@app.get("/api/v1/audit/verify-chain", response_model=AuditChainIntegrityReport)
def verify_chain_integrity():
    if len(AUDIT_LOG_STORE) == 0:
        return AuditChainIntegrityReport(
            total_events=0,
            valid_chain=True,
            last_hash=GENESIS_HASH,
            verified_at=str(int(time.time()))
        )

    expected_prev = GENESIS_HASH
    for i, event in enumerate(AUDIT_LOG_STORE):
        if event.prev_hash != expected_prev:
            return AuditChainIntegrityReport(
                total_events=len(AUDIT_LOG_STORE),
                valid_chain=False,
                tampered_index=i,
                last_hash=event.current_hash,
                verified_at=str(int(time.time()))
            )

        calc_hash = _compute_event_hash(
            event.sequence_number,
            event.event_id,
            event.actor_id,
            event.action,
            event.resource_id,
            event.payload_hash,
            event.prev_hash,
            event.timestamp
        )

        if calc_hash != event.current_hash:
            return AuditChainIntegrityReport(
                total_events=len(AUDIT_LOG_STORE),
                valid_chain=False,
                tampered_index=i,
                last_hash=event.current_hash,
                verified_at=str(int(time.time()))
            )

        expected_prev = event.current_hash

    return AuditChainIntegrityReport(
        total_events=len(AUDIT_LOG_STORE),
        valid_chain=True,
        last_hash=AUDIT_LOG_STORE[-1].current_hash,
        verified_at=str(int(time.time()))
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007)
