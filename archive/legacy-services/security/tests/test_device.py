import pytest
from services.security.app.services.device_service import DeviceService


@pytest.mark.asyncio
async def test_multi_account_device_signal():
    svc = DeviceService()
    dev_ref = "dev-shared-ref-100"

    await svc.link_user(dev_ref, "user-1")
    res2 = await svc.link_user(dev_ref, "user-2")
    assert res2["risk_signal"] is None

    res3 = await svc.link_user(dev_ref, "user-3")
    assert res3["risk_signal"] is not None
    assert res3["risk_signal"]["signal_type"] == "MULTI_ACCOUNT_DEVICE"
