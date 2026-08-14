"""Delivery assignment service."""

from __future__ import annotations

import math
from ..domain.enums import DeliveryStatus
from ..models.courier import Courier
from ..models.delivery import Delivery


class DeliveryAssignmentService:
    """Algorithm service selecting best active courier for delivery assignment."""

    async def assign(self, delivery: Delivery, couriers: list[Courier]) -> Delivery:
        """Assign best active courier to delivery."""
        available = [c for c in couriers if c.active]
        if not available:
            raise ValueError("No courier available")

        best_courier = self.select_best(available)
        delivery.courier_id = best_courier.id
        delivery.status = DeliveryStatus.ASSIGNED
        return delivery

    def select_best(self, couriers: list[Courier]) -> Courier:
        """Select courier minimizing distance metric."""
        return min(couriers, key=lambda c: self.distance_to_delivery(c))

    def distance_to_delivery(self, courier: Courier) -> float:
        """Compute Euclidean distance for courier coordinates."""
        lat = courier.latitude or 0.0
        lon = courier.longitude or 0.0
        return math.sqrt(lat**2 + lon**2)
