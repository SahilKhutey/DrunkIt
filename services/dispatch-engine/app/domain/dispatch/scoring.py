from math import atan2, cos, radians, sin, sqrt


EARTH_RADIUS_KM = 6371.0

AVERAGE_SPEED_KMH = {
    "BIKE": 25,
    "SCOOTER": 30,
    "CAR": 35,
    "VAN": 30,
}


def haversine_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:

    lat1 = radians(lat1)
    lat2 = radians(lat2)

    delta_lat = radians(lat2 - lat1)
    delta_lon = radians(lon2 - lon1)

    a = (
        sin(delta_lat / 2) ** 2
        + cos(lat1)
        * cos(lat2)
        * sin(delta_lon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a),
    )

    return EARTH_RADIUS_KM * c


def estimate_pickup_minutes(
    distance_km: float,
    vehicle_type: str,
) -> float:

    speed = AVERAGE_SPEED_KMH.get(
        vehicle_type,
        25,
    )

    hours = distance_km / speed

    return hours * 60


def calculate_driver_score(
    distance_km: float,
    eta_minutes: float,
) -> float:

    distance_component = max(
        0.0,
        1.0 - (distance_km / 10.0),
    )

    eta_component = max(
        0.0,
        1.0 - (eta_minutes / 30.0),
    )

    score = (
        distance_component * 0.55
        + eta_component * 0.45
    )

    return round(score, 6)
