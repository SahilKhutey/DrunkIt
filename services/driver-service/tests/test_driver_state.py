import os
import sys
import pytest

service_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
if service_dir not in sys.path:
    sys.path.insert(0, service_dir)

for mod in list(sys.modules.keys()):
    if mod == "app" or mod.startswith("app."):
        del sys.modules[mod]

from app.domain.driver.enums import (
    DriverOperationalStatus,
)

from app.domain.driver.state_machine import (
    can_transition,
    validate_transition,
)



def test_offline_to_available():

    assert can_transition(
        DriverOperationalStatus.OFFLINE,
        DriverOperationalStatus.AVAILABLE,
    )


def test_available_to_reserved():

    assert can_transition(
        DriverOperationalStatus.AVAILABLE,
        DriverOperationalStatus.RESERVED,
    )


def test_available_to_delivering_is_invalid():

    assert not can_transition(
        DriverOperationalStatus.AVAILABLE,
        DriverOperationalStatus.DELIVERING,
    )


def test_invalid_transition_raises():

    with pytest.raises(ValueError):

        validate_transition(
            DriverOperationalStatus.OFFLINE,
            DriverOperationalStatus.DELIVERING,
        )
