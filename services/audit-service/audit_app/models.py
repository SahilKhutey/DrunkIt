from pydantic import BaseModel
from typing import Optional, Dict, Any

class AuditEventCreate(BaseModel):
    event_type: str
    actor_id: str
    actor_type: str
    action: str
    resource_id: str
    resource_type: str
    jurisdiction: str
    policy_version: Optional[str] = "1.0"
    payload: Dict[str, Any]

class AuditEventRecord(BaseModel):
    sequence_number: int
    event_id: str
    event_type: str
    actor_id: str
    actor_type: str
    action: str
    resource_id: str
    resource_type: str
    jurisdiction: str
    policy_version: Optional[str] = "1.0"
    payload_hash: str
    prev_hash: str
    current_hash: str
    timestamp: str

class AuditChainIntegrityReport(BaseModel):
    total_events: int
    valid_chain: bool
    tampered_index: Optional[int] = None
    last_hash: str
    verified_at: str
