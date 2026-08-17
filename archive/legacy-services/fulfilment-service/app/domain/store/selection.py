from pydantic import BaseModel


class StoreCandidate(BaseModel):

    store_id: str

    distance_km: float

    inventory_score: float

    capacity_score: float

    total_score: float


def calculate_store_score(
    distance_km: float,
    inventory_score: float,
    capacity_score: float,
) -> float:

    distance_score = max(
        0.0,
        1.0 - distance_km / 10.0,
    )

    return round(
        (
            distance_score * 0.45
            + inventory_score * 0.35
            + capacity_score * 0.20
        ),
        6,
    )
