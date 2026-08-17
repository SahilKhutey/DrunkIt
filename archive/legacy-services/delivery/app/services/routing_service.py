class RoutingService:

    async def distance_to_delivery(self, rider: dict, delivery: dict) -> float | None:
        # Mock calculation: returns distance in meters (e.g. 1500m)
        return 1500.0

    async def calculate_eta(self, distance_meters: float) -> int:
        # Speed ~ 30 km/h = 8.33 m/s -> 1500 / 8.33 = ~180 seconds
        return int(distance_meters / 8.33)
