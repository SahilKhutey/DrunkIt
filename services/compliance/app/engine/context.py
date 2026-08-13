from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class ComplianceContext:

    consumer_id: UUID | str | None

    retailer_id: UUID | str | None

    rider_id: UUID | str | None

    product_id: UUID | str | None

    order_id: UUID | str | None

    delivery_id: UUID | str | None

    jurisdiction_id: str

    operation: str

    timestamp: datetime
