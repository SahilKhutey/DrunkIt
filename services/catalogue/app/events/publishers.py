class CatalogueEventPublisher:

    def __init__(self, producer=None):
        self.producer = producer

    async def product_created(self, product: dict):
        if self.producer:
            await self.producer.publish(
                topic="catalogue.product.created",
                key=str(product.get("id")),
                value={
                    "event": "catalogue.product.created",
                    "product_id": str(product.get("id")),
                },
            )

    async def listing_approved(self, listing: dict):
        if self.producer:
            await self.producer.publish(
                topic="catalogue.listing.approved",
                key=str(listing.get("id")),
                value={
                    "event": "catalogue.listing.approved",
                    "listing_id": str(listing.get("id")),
                },
            )
