import uuid

from app.domain.serviceability.geo import (
    distance_km,
)

from app.domain.store.selection import (
    calculate_store_score,
    StoreCandidate,
)

from app.repositories.store import (
    StoreRepository,
)

from app.schemas.fulfilment import (
    FulfilmentRequest,
    FulfilmentPlan,
)

from app.services.inventory import (
    InventoryService,
)


class FulfilmentPlanner:

    def __init__(self, store_repository=None, inventory_service=None):

        self.store_repository = store_repository or (
            StoreRepository()
        )

        self.inventory_service = inventory_service or (
            InventoryService()
        )

    async def create_plan(
        self,
        request: FulfilmentRequest,
    ) -> FulfilmentPlan:

        stores = (
            await self.store_repository
            .list_active()
        )

        candidates = []

        for store in stores:

            if (
                request.requested_store_id
                and store.store_id
                != request.requested_store_id
            ):
                continue

            distance = distance_km(

                request.customer_location.latitude,

                request.customer_location.longitude,

                store.location.latitude,

                store.location.longitude,
            )

            if (
                distance
                > store.service_radius_km
            ):
                continue

            inventory_ok = True

            available_count = 0
            required_count = 0

            for item in request.items:

                required_count += item.quantity

                available = (
                    await self.inventory_service
                    .has_quantity(
                        store.store_id,
                        item.product_id,
                        item.quantity,
                    )
                )

                if not available:
                    inventory_ok = False
                    break

                inventory_item = (
                    await self.inventory_service
                    .get_item(
                        store.store_id,
                        item.product_id,
                    )
                )

                available_count += (
                    inventory_item
                    .sellable_quantity
                )

            if not inventory_ok:
                continue

            inventory_score = min(
                1.0,
                available_count
                / max(required_count, 1),
            )

            capacity_score = 1.0

            score = calculate_store_score(
                distance,
                inventory_score,
                capacity_score,
            )

            candidates.append(
                StoreCandidate(
                    store_id=store.store_id,
                    distance_km=distance,
                    inventory_score=inventory_score,
                    capacity_score=capacity_score,
                    total_score=score,
                )
            )

        if not candidates:

            raise ValueError(
                "No fulfilment store available"
            )

        candidates.sort(
            key=lambda candidate:
                candidate.total_score,
            reverse=True,
        )

        selected = candidates[0]

        store = await self.store_repository.get(
            selected.store_id
        )

        return FulfilmentPlan(
            plan_id=str(uuid.uuid4()),
            order_id=request.order_id,
            store_id=store.store_id,
            retailer_id=store.retailer_id,
            items=request.items,
            status="STORE_SELECTED",
            serviceable=True,
            compliance_status="APPROVED",
            estimated_delivery_minutes=max(
                5,
                int(
                    selected.distance_km
                    * 4
                ),
            ),
        )
