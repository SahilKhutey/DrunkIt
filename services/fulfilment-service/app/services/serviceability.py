from app.core.exceptions import (
    ServiceabilityReason,
)

from app.domain.serviceability.geo import (
    distance_km,
)

from app.repositories.store import (
    StoreRepository,
)

from app.schemas.serviceability import (
    ServiceabilityRequest,
)


class ServiceabilityService:

    def __init__(self, store_repository=None):

        self.store_repository = store_repository or (
            StoreRepository()
        )

    async def check(
        self,
        request: ServiceabilityRequest,
    ):

        stores = (
            await self.store_repository
            .list_active()
        )

        eligible = []

        for store in stores:

            distance = distance_km(

                request.customer_location.latitude,

                request.customer_location.longitude,

                store.location.latitude,

                store.location.longitude,
            )

            if (
                distance
                <= store.service_radius_km
            ):

                eligible.append(
                    (
                        store,
                        distance,
                    )
                )

        if not eligible:

            return {
                "serviceable": False,
                "reason": (
                    ServiceabilityReason
                    .NO_STORE_AVAILABLE
                ),
                "zone_id": None,
                "available_store_count": 0,
            }

        return {
            "serviceable": True,
            "reason": None,
            "zone_id": "ZONE-001",
            "available_store_count": len(
                eligible
            ),
        }
