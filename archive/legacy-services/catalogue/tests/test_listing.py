import pytest
from services.catalogue.app.domain.state import validate_transition
from services.catalogue.app.services.listing_service import ListingService


def test_product_state_transitions():
    assert validate_transition("DRAFT", "SUBMITTED") is True
    assert validate_transition("APPROVED", "ACTIVE") is True

    with pytest.raises(ValueError, match="Invalid transition"):
        validate_transition("DRAFT", "ACTIVE")


@pytest.mark.asyncio
async def test_listing_approval():
    service = ListingService()
    approved = await service.approve("LIST-100", "MAHARASHTRA")
    assert approved["status"] == "APPROVED"
