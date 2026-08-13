import os
import sys
from unittest.mock import AsyncMock, patch
import pytest

service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

for mod in list(sys.modules.keys()):
    if mod == "app" or mod.startswith("app."):
        del sys.modules[mod]

import app.api.drivers as app_drivers
from app.domain.driver.enums import (
    DriverAccountStatus,
    DriverOperationalStatus,
    VehicleType,
    VerificationStatus,
)
from app.domain.driver.models import Driver
from app.main import app as fastapi_app

from fastapi.testclient import TestClient

client = TestClient(fastapi_app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "driver-service"


def test_create_driver_api():
    with patch.object(app_drivers, "DriverService") as mock_service_class:
        mock_service_instance = AsyncMock()
        mock_service_class.return_value = mock_service_instance

        mock_driver = Driver(
            id="drv_123",
            user_id="usr_driver_101",
            name="Alex Driver",
            phone="+919876543210",
            account_status=DriverAccountStatus.PENDING,
            operational_status=DriverOperationalStatus.OFFLINE,
            verification_status=VerificationStatus.PENDING,
            vehicle_type=VehicleType.BIKE,
            latitude=None,
            longitude=None,
            location_updated_at=None,
        )
        mock_service_instance.create_driver.return_value = mock_driver

        payload = {
            "user_id": "usr_driver_101",
            "name": "Alex Driver",
            "phone": "+919876543210",
            "vehicle_type": "BIKE",
        }

        response = client.post("/api/v1/drivers", json=payload)
        assert response.status_code == 201
        res_data = response.json()
        assert res_data["id"] == "drv_123"
        assert res_data["account_status"] == "PENDING"
        assert res_data["operational_status"] == "OFFLINE"
