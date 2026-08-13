import os
import sys

service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

for mod in list(sys.modules.keys()):
    if mod == "app" or mod.startswith("app."):
        del sys.modules[mod]

from app.domain.dispatch.scoring import (
    calculate_driver_score,
    haversine_distance_km,
)


def test_same_location_distance():

    distance = haversine_distance_km(
        21.1702,
        72.8311,
        21.1702,
        72.8311,
    )

    assert distance == 0


def test_distance_positive():

    distance = haversine_distance_km(
        21.1702,
        72.8311,
        21.1802,
        72.8411,
    )

    assert distance > 0


def test_score_range():

    score = calculate_driver_score(
        1.0,
        5.0,
    )

    assert 0 <= score <= 1


def test_closer_driver_scores_higher():

    close = calculate_driver_score(
        1.0,
        3.0,
    )

    far = calculate_driver_score(
        8.0,
        20.0,
    )

    assert close > far
