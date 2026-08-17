from app.core.config import settings

from app.domain.dispatch.scoring import (
    calculate_driver_score,
    estimate_pickup_minutes,
    haversine_distance_km,
)

from app.schemas.dispatch import (
    DispatchRequest,
    DriverScore,
)

from app.services.delivery_client import (
    DeliveryServiceClient,
)

from app.services.driver_client import (
    DriverServiceClient,
)


class DispatchService:

    def __init__(self, driver_client=None, delivery_client=None):

        self.driver_client = driver_client or (
            DriverServiceClient()
        )

        self.delivery_client = delivery_client or (
            DeliveryServiceClient()
        )

    async def dispatch(
        self,
        request: DispatchRequest,
    ):

        # --------------------------------------------------
        # 1. Move delivery into dispatching
        # --------------------------------------------------

        await self.delivery_client.move_to_dispatching(
            request.delivery_id
        )

        # --------------------------------------------------
        # 2. Discover available drivers
        # --------------------------------------------------

        drivers = (
            await self.driver_client
            .get_available_drivers()
        )

        candidates: list[DriverScore] = []

        # --------------------------------------------------
        # 3. Filter and score
        # --------------------------------------------------

        for driver in drivers:

            if (
                request.required_vehicle_type
                and driver.vehicle_type
                != request.required_vehicle_type
            ):
                continue

            if (
                driver.latitude is None
                or driver.longitude is None
            ):
                continue

            distance = haversine_distance_km(
                request.pickup_location.latitude,
                request.pickup_location.longitude,
                driver.latitude,
                driver.longitude,
            )

            if (
                distance
                > settings.max_driver_distance_km
            ):
                continue

            eta = estimate_pickup_minutes(
                distance,
                driver.vehicle_type,
            )

            score = calculate_driver_score(
                distance,
                eta,
            )

            candidates.append(
                DriverScore(
                    driver_id=driver.driver_id,
                    distance_km=distance,
                    estimated_pickup_minutes=eta,
                    score=score,
                )
            )

        # --------------------------------------------------
        # 4. Rank candidates
        # --------------------------------------------------

        candidates.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        candidates = candidates[
            : settings.candidate_limit
        ]

        # --------------------------------------------------
        # 5. Try candidates sequentially
        # --------------------------------------------------

        for candidate in candidates:

            reserved = (
                await self.driver_client
                .reserve_driver(
                    candidate.driver_id,
                    request.delivery_id,
                )
            )

            if not reserved:
                continue

            # ----------------------------------------------
            # 6. Assign driver to delivery
            # ----------------------------------------------

            await self.delivery_client.assign_driver(
                request.delivery_id,
                candidate.driver_id,
            )

            # ----------------------------------------------
            # 7. Move delivery to ASSIGNED
            # ----------------------------------------------

            delivery = (
                await self.delivery_client
                .move_to_assigned(
                    request.delivery_id
                )
            )

            return {
                "delivery_id": request.delivery_id,
                "driver_id": candidate.driver_id,
                "status": delivery.get("status", "ASSIGNED"),
                "score": candidate.score,
                "distance_km": candidate.distance_km,
                "pickup_eta_minutes": (
                    candidate.estimated_pickup_minutes
                ),
            }

        raise RuntimeError(
            "No eligible driver available"
        )
