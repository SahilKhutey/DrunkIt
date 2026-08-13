from datetime import datetime, timezone

from packages.audit.model import AuditLog


async def record_audit(
    session,
    actor_type: str,
    actor_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    metadata: dict,
):

    event = AuditLog(

        actor_type=actor_type,

        actor_id=actor_id,

        action=action,

        resource_type=resource_type,

        resource_id=resource_id,

        metadata=metadata,

        created_at=datetime.now(
            timezone.utc
        ),
    )

    session.add(event)
