import json

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.delivery.enums import (
    ActorType,
    DeliveryStatus,
)
from app.domain.delivery.event_model import DeliveryEvent
from app.domain.delivery.models import Delivery
from app.domain.delivery.state_machine import (
    validate_transition,
)
from app.repositories.delivery import DeliveryRepository
from app.schemas.delivery import DeliveryCreate


class DeliveryService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = DeliveryRepository(session)

    async def create_delivery(
        self,
        data: DeliveryCreate,
    ) -> Delivery:

        existing = await self.repository.get_by_order_id(
            data.order_id
        )

        if existing:
            raise ValueError(
                "Delivery already exists for this order"
            )

        delivery = Delivery(
            order_id=data.order_id,
            retailer_id=data.retailer_id,
            store_id=data.store_id,
            consumer_id=data.consumer_id,
            pickup_address=data.pickup_address,
            dropoff_address=data.dropoff_address,
            status=DeliveryStatus.REQUESTED,
        )

        await self.repository.create(delivery)

        await self._record_event(
            delivery=delivery,
            event_type="DELIVERY_REQUESTED",
            actor_type=ActorType.SYSTEM,
            actor_id=None,
        )

        await self.session.commit()

        return delivery

    async def transition(
        self,
        delivery: Delivery,
        target: DeliveryStatus,
        actor_type: ActorType,
        actor_id: str | None = None,
    ) -> Delivery:

        validate_transition(
            delivery.status,
            target,
        )

        previous = delivery.status

        delivery.status = target

        await self._record_event(
            delivery=delivery,
            event_type=f"DELIVERY_{target.value}",
            actor_type=actor_type,
            actor_id=actor_id,
            payload={
                "previous_status": previous.value,
                "new_status": target.value,
            },
        )

        await self.session.commit()

        return delivery

    async def assign_driver(
        self,
        delivery: Delivery,
        driver_id: str,
    ) -> Delivery:

        if delivery.status != DeliveryStatus.DISPATCHING:
            raise ValueError(
                "Driver can only be assigned during dispatching"
            )

        delivery.driver_id = driver_id

        await self._record_event(
            delivery=delivery,
            event_type="DRIVER_ASSIGNED",
            actor_type=ActorType.SYSTEM,
            actor_id=None,
            payload={
                "driver_id": driver_id,
            },
        )

        await self.session.commit()

        return delivery

    async def _record_event(
        self,
        delivery: Delivery,
        event_type: str,
        actor_type: ActorType,
        actor_id: str | None,
        payload: dict | None = None,
    ):

        event = DeliveryEvent(
            delivery_id=delivery.id,
            event_type=event_type,
            actor_type=actor_type.value,
            actor_id=actor_id,
            payload=json.dumps(payload or {}),
        )

        self.session.add(event)
