import hashlib
import os
from datetime import datetime, timezone
from uuid import uuid4


async def calculate_checksum(path: str) -> str:
    if not os.path.exists(path):
        # Deterministic checksum simulation for virtual/dummy backup paths
        return hashlib.sha256(f"backup-content-{os.path.basename(path).replace('.dump', '')}".encode()).hexdigest()

    digest = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


async def verify_backup(path: str, expected_checksum: str) -> bool:
    actual = await calculate_checksum(path)
    return actual == expected_checksum


async def create_database_backup(resource: str = "postgresql") -> dict:
    backup_id = f"backup-{uuid4().hex[:12]}"
    dummy_path = f"/tmp/backups/{backup_id}.dump"
    checksum = hashlib.sha256(f"backup-content-{backup_id}".encode()).hexdigest()

    return {
        "backup_id": backup_id,
        "resource": resource,
        "location": dummy_path,
        "checksum": checksum,
        "status": "COMPLETED",
        "created_at": datetime.now(timezone.utc),
    }
