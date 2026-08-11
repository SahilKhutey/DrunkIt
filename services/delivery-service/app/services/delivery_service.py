from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from faccp_common.exceptions import InvalidCredentialsError, NotFoundError
from faccp_common.security import generate_otp
from app.db.models import DeliveryTask
from app.schemas.delivery import CreateTaskRequest, TaskResponse, VerifyHandoverRequest


class DeliveryService:

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_task(self, req: CreateTaskRequest) -> TaskResponse:
        task = DeliveryTask(
            order_id=req.order_id,
            status="UNASSIGNED",
            otp_code=generate_otp(6),
        )
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)

        return TaskResponse(
            id=task.id,
            order_id=task.order_id,
            driver_id=task.driver_id,
            status=task.status,
            otp_code=task.otp_code,
            delivered_at=task.delivered_at,
        )

    async def verify_handover(self, req: VerifyHandoverRequest) -> TaskResponse:
        res = await self.db.execute(
            select(DeliveryTask).where(DeliveryTask.order_id == req.order_id)
        )
        task = res.scalar_one_or_none()
        if not task:
            raise NotFoundError("Delivery task not found.")

        if task.otp_code != req.otp_code:
            raise InvalidCredentialsError("Invalid handover OTP code.")

        task.status = "DELIVERED"
        task.delivered_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(task)

        return TaskResponse(
            id=task.id,
            order_id=task.order_id,
            driver_id=task.driver_id,
            status=task.status,
            otp_code=task.otp_code,
            delivered_at=task.delivered_at,
        )
