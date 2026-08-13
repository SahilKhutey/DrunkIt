from app.domain.serviceability.geo import (
    distance_km,
)


def within_service_radius(
    customer_lat: float,
    customer_lon: float,
    store_lat: float,
    store_lon: float,
    radius_km: float,
) -> bool:

    distance = distance_km(
        customer_lat,
        customer_lon,
        store_lat,
        store_lon,
    )

    return distance <= radius_km
