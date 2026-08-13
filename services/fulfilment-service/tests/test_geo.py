import os
import sys

service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

for mod in list(sys.modules.keys()):
    if mod == "app" or mod.startswith("app."):
        del sys.modules[mod]

from app.domain.serviceability.geo import (
    distance_km,
)


def test_same_point():

    assert distance_km(
        21.1702,
        72.8311,
        21.1702,
        72.8311,
    ) == 0


def test_distance_is_positive():

    result = distance_km(
        21.1702,
        72.8311,
        21.1802,
        72.8411,
    )

    assert result > 0
