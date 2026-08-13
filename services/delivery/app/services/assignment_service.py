from datetime import datetime, timezone
from uuid import uuid4

from services.delivery.app.services.dispatch_service import DispatchService
from services.delivery.app.services.routing_service import RoutingService


class AssignmentService:

    def __init__(
        self,
        dispatch_service: DispatchService | None = None,
        routing_service: RoutingService | None = None,
    ):
        self.dispatch_service = dispatch_service or DispatchService()
        self.routing = routing_service or RoutingService()

        self.riders: dict[str, dict] = {}
        self.assignments: dict[str, dict] = {}

    def score_candidate(self, candidate: dict) -> float:
        distance = candidate["distance"]
        return 100000.0 - distance

    async def find_candidates(self, delivery: dict) -> list[dict]:
        candidates = []
        for rider in self.riders.values():
            if rider["verification_status"] != "ACTIVE":
                continue
            if rider["status"] != "AVAILABLE" or rider.get("active_delivery_id"):
                continue

            distance = await self.routing.distance_to_delivery(rider, delivery)
            if distance is None or distance > 5000:
                continue

            candidates.append({"rider": rider, "distance": distance})
        return candidates

    async def assign_rider(self, delivery_id: str) -> dict:
        delivery = self.dispatch_service.deliveries.get(delivery_id)
        if not delivery:
            raise ValueError("DELIVERY_NOT_FOUND")

        if delivery["status"] != "ASSIGNMENT_PENDING":
            raise ValueError("INVALID_ASSIGNMENT_STATE")

        candidates = await self.find_candidates(delivery)
        if not candidates:
            raise ValueError("NO_RIDER_AVAILABLE")

        best = max(candidates, key=self.score_candidate)
        rider = best["rider"]

        assignment_id = str(uuid4())
        assignment = {
            "id": assignment_id,
            "delivery_id": delivery_id,
            "rider_id": rider["id"],
            "status": "ASSIGNED",
            "distance_meters": int(best["distance"]),
            "estimated_seconds": await self.routing.calculate_eta(best["distance"]),
            "created_at": datetime.now(timezone.utc),
        }
        self.assignments[assignment_id] = assignment

        rider["active_delivery_id"] = delivery_id
        rider["status"] = "BUSY"

        await self.dispatch_service.transition(delivery, "ASSIGNED")
        return assignment
