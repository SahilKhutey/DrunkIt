from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.delivery.models import Delivery


class DeliveryRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        delivery: Delivery,
    ) -> Delivery:
        self.session.add(delivery)
        await self.session.flush()
        await self.session.refresh(delivery)

        return delivery

    async def get_by_id(
        self,
        delivery_id: str,
    ) -> Delivery | None:

        result = await self.session.execute(
            select(Delivery).where(
                Delivery.id == delivery_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_order_id(
        self,
        order_id: str,
    ) -> Delivery | None:

        result = await self.session.execute(
            select(Delivery).where(
                Delivery.order_id == order_id
            )
        )

        return result.scalar_one_or_none()
