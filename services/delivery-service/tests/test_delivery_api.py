import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch
import pytest

service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.insert(0, service_dir)
for mod in list(sys.modules.keys()):
    if mod == "app" or mod.startswith("app."):
        del sys.modules[mod]

from fastapi.testclient import TestClient




from app.domain.delivery.enums import DeliveryStatus
from app.domain.delivery.models import Delivery
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "delivery-engine"


@patch("app.api.delivery.DeliveryService")
def test_create_delivery_api(mock_service_class):
    mock_service_instance = AsyncMock()
    mock_service_class.return_value = mock_service_instance

    mock_delivery = Delivery(
        id="del_123",
        order_id="ord_123",
        retailer_id="ret_1",
        store_id="str_1",
        consumer_id="con_1",
        pickup_address="123 Store St",
        dropoff_address="456 Home Ave",
        status=DeliveryStatus.REQUESTED,
    )
    mock_service_instance.create_delivery.return_value = mock_delivery

    payload = {
        "order_id": "ord_123",
        "retailer_id": "ret_1",
        "store_id": "str_1",
        "consumer_id": "con_1",
        "pickup_address": "123 Store St",
        "dropoff_address": "456 Home Ave",
    }

    response = client.post("/api/v1/deliveries", json=payload)
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["id"] == "del_123"
    assert res_data["status"] == "REQUESTED"
