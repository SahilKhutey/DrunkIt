from services.catalogue.app.services.catalogue_service import CatalogueService


class ListingService:

    def __init__(
        self,
        catalogue_service: CatalogueService | None = None,
        listing_repository=None,
    ):
        self.catalogue = catalogue_service or CatalogueService()
        self.repository = listing_repository or {}

    async def approve(
        self,
        listing_id: str,
        jurisdiction: str,
    ) -> dict:

        listing = self.repository.get(listing_id, {
            "id": listing_id,
            "sku_id": "SKU-001",
            "retailer_id": "RET-001",
            "store_id": "STORE-001",
            "status": "PENDING_REVIEW",
        })

        eligibility = await self.catalogue.can_list(
            sku_id=listing["sku_id"],
            retailer_id=listing["retailer_id"],
            store_id=listing["store_id"],
            jurisdiction=jurisdiction,
        )

        if not eligibility["allowed"]:
            listing["status"] = "BLOCKED"
            raise PermissionError(eligibility["reason"])

        listing["status"] = "APPROVED"
        self.repository[listing_id] = listing
        return listing
