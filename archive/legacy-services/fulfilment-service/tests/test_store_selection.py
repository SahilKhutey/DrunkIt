import os
import sys

service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

for mod in list(sys.modules.keys()):
    if mod == "app" or mod.startswith("app."):
        del sys.modules[mod]

from app.domain.store.selection import (
    calculate_store_score,
)


def test_store_score():

    score = calculate_store_score(
        distance_km=1.0,
        inventory_score=1.0,
        capacity_score=1.0,
    )

    assert score > 0.9
