from datetime import datetime
from pydantic import BaseModel, Field


class InventoryItem(BaseModel):

    product_id: str

    store_id: str

    quantity_available: int = Field(
        ge=0
    )

    reserved_quantity: int = Field(
        ge=0
    )

    active: bool = True

    @property
    def sellable_quantity(self) -> int:

        return max(
            0,
            self.quantity_available
            - self.reserved_quantity,
        )


class InventoryReservation(BaseModel):

    reservation_id: str

    order_id: str

    store_id: str

    product_id: str

    quantity: int

    status: str  # ACTIVE, CONFIRMED, EXPIRED, RELEASED

    expires_at: datetime
