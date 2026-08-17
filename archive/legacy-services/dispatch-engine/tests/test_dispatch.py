import os
import sys
from unittest.mock import AsyncMock
import pytest

service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

for mod in list(sys.modules.keys()):
    if mod == "app" or mod.startswith("app."):
        del sys.modules[mod]

from app.schemas.dispatch import (
    DispatchRequest,
    DriverCandidate,
    Location,
)
from app.services.dispatch import DispatchService


@pytest.mark.asyncio
async def test_dispatch_service_flow():

    mock_driver_client = AsyncMock()
    mock_delivery_client = AsyncMock()

    mock_driver_client.get_available_drivers.return_value = [
        DriverCandidate(
            driver_id="drv_001",
            vehicle_type="BIKE",
            latitude=21.1720,
            longitude=72.8330,
        ),
        DriverCandidate(
            driver_id="drv_002",
            vehicle_type="BIKE",
            latitude=21.1900,
            longitude=72.8500,
        ),
    ]

    mock_driver_client.reserve_driver.return_value = True
    mock_delivery_client.move_to_dispatching.return_value = {"status": "DISPATCHING"}
    mock_delivery_client.assign_driver.return_value = {"status": "DISPATCHING"}
    mock_delivery_client.move_to_assigned.return_value = {"status": "ASSIGNED"}

    dispatch_service = DispatchService(
        driver_client=mock_driver_client,
        delivery_client=mock_delivery_client,
    )

    request = DispatchRequest(
        delivery_id="del_1001",
        pickup_location=Location(latitude=21.1702, longitude=72.8311),
        required_vehicle_type="BIKE",
    )

    result = await dispatch_service.dispatch(request)

    assert result["delivery_id"] == "del_1001"
    assert result["driver_id"] == "drv_001"
    assert result["status"] == "ASSIGNED"
    assert result["score"] > 0
