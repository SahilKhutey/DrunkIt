from __future__ import annotations

import uuid
from app.schemas.notification import SendNotificationRequest, SendNotificationResponse


class NotificationService:

    async def send(self, req: SendNotificationRequest) -> SendNotificationResponse:
        return SendNotificationResponse(
            message_id=f"msg_{uuid.uuid4().hex[:16]}",
            recipient=req.recipient,
            channel=req.channel,
            status="DELIVERED",
        )
