from fastapi import APIRouter, status
from faccp_common.dto import APIResponse
from app.schemas.notification import SendNotificationRequest, SendNotificationResponse
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/send", status_code=status.HTTP_201_CREATED)
async def send_notification(
    payload: SendNotificationRequest,
) -> APIResponse[SendNotificationResponse]:
    svc = NotificationService()
    res = await svc.send(payload)
    return APIResponse(data=res)
