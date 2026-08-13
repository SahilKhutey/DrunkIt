from app.schemas.location import GeoLocation
from app.schemas.store import Store


class StoreRepository:

    def __init__(self):

        self._stores = [

            Store(
                store_id="STORE-001",
                retailer_id="RET-001",
                name="Retail Store 001",
                location=GeoLocation(
                    latitude=21.1702,
                    longitude=72.8311,
                ),
                service_radius_km=5.0,
                active=True,
                accepting_orders=True,
            ),

            Store(
                store_id="STORE-002",
                retailer_id="RET-002",
                name="Retail Store 002",
                location=GeoLocation(
                    latitude=21.1802,
                    longitude=72.8411,
                ),
                service_radius_km=7.0,
                active=True,
                accepting_orders=True,
            ),
        ]

    async def list_active(self):

        return [
            store
            for store in self._stores
            if store.active
            and store.accepting_orders
        ]

    async def get(
        self,
        store_id: str,
    ):

        for store in self._stores:

            if store.store_id == store_id:
                return store

        return None
