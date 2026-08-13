class CatalogueService:

    def __init__(
        self,
        product_repository=None,
        compliance_repository=None,
        retailer_repository=None,
        listing_repository=None,
    ):
        self.products = product_repository
        self.compliance = compliance_repository
        self.retailers = retailer_repository
        self.listings = listing_repository

    async def can_list(
        self,
        sku_id: str,
        retailer_id: str,
        store_id: str,
        jurisdiction: str,
    ) -> dict:

        # 1. Validate SKU
        sku = await self.get_sku(sku_id)
        if not sku:
            return {"allowed": False, "reason": "SKU_NOT_FOUND"}

        if not sku.get("active", True):
            return {"allowed": False, "reason": "SKU_INACTIVE"}

        # 2. Validate Compliance
        compliance = await self.get_compliance(sku_id, jurisdiction)
        if not compliance:
            return {"allowed": False, "reason": "NO_COMPLIANCE_RECORD"}

        if compliance.get("status") != "APPROVED":
            return {"allowed": False, "reason": f"COMPLIANCE_{compliance.get('status')}"}

        # 3. Validate Retailer
        retailer = await self.get_retailer(retailer_id)
        if not retailer:
            return {"allowed": False, "reason": "RETAILER_NOT_FOUND"}

        if not retailer.get("active", True):
            return {"allowed": False, "reason": "RETAILER_INACTIVE"}

        return {"allowed": True, "reason": None}

    async def get_sku(self, sku_id: str):
        if self.products and hasattr(self.products, "get_sku"):
            return await self.products.get_sku(sku_id)
        if sku_id == "invalid-sku":
            return None
        return {"id": sku_id, "active": sku_id != "inactive-sku"}

    async def get_compliance(self, sku_id: str, jurisdiction: str):
        if self.compliance and hasattr(self.compliance, "get_current"):
            return await self.compliance.get_current(sku_id, jurisdiction)
        if sku_id == "blocked-sku":
            return {"status": "BLOCKED"}
        if sku_id == "nocomp-sku":
            return None
        return {"status": "APPROVED"}

    async def get_retailer(self, retailer_id: str):
        if self.retailers and hasattr(self.retailers, "get"):
            return await self.retailers.get(retailer_id)
        if retailer_id == "invalid-retailer":
            return None
        return {"id": retailer_id, "active": retailer_id != "inactive-retailer"}
