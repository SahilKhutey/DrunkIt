"""Unit test for Consumer domain service duplicate detection."""

import uuid
import pytest
from services.consumer.app.domain.enums import ConsumerStatus
from services.consumer.app.services.consumer_service import ConsumerService


class FakeConsumerRepository:
    def __init__(self):
        self.consumer = None

    async def get_by_identity(self, identity_id):
        if self.consumer and str(self.consumer.identity_id) == str(identity_id):
            return self.consumer
        return None

    async def create(self, identity_id):
        self.consumer = type(
            "Consumer",
            (),
            {
                "id": uuid.uuid4(),
                "identity_id": str(identity_id),
                "status": ConsumerStatus.PENDING,
                "version": 1,
            },
        )()
        return self.consumer


@pytest.mark.asyncio
async def test_duplicate_consumer_rejected():
    repository = FakeConsumerRepository()
    service = ConsumerService(repository)
    identity_id = uuid.uuid4()

    created = await service.create(identity_id)
    assert created.identity_id == str(identity_id)

    with pytest.raises(ValueError, match="Consumer already exists"):
        await service.create(identity_id)
