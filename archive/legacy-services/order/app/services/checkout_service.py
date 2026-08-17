from datetime import datetime, timezone
from uuid import uuid4

from services.order.app.clients.catalogue_client import CatalogueClient
from services.order.app.clients.inventory_client import InventoryClient
from services.order.app.schemas.checkout import CheckoutRequest
from services.order.app.services.cart_service import CartService
from services.order.app.services.eligibility_service import EligibilityService
from services.order.app.services.pricing_service import PricingService


class CheckoutService:

    def __init__(
        self,
        cart_service: CartService | None = None,
        catalogue_client: CatalogueClient | None = None,
        inventory_client: InventoryClient | None = None,
        eligibility_service: EligibilityService | None = None,
        pricing_service: PricingService | None = None,
    ):
        self.cart_service = cart_service or CartService()
        self.catalogue = catalogue_client or CatalogueClient()
        self.inventory = inventory_client or InventoryClient()
        self.eligibility = eligibility_service or EligibilityService()
        self.pricing = pricing_service or PricingService()

        self.orders: dict[str, dict] = {}
        self.idempotency_map: dict[str, dict] = {}

    async def checkout(self, request: CheckoutRequest) -> dict:
        # 1. Idempotency Check
        if request.idempotency_key in self.idempotency_map:
            return self.idempotency_map[request.idempotency_key]

        # 2. Load Cart
        cart = self.cart_service.carts.get(request.cart_id)
        if not cart or cart["customer_id"] != request.customer_id:
            raise ValueError("CART_NOT_FOUND")

        items = self.cart_service.cart_items.get(request.cart_id, [])
        if not items:
            raise ValueError("CART_EMPTY")

        # 3. Store Validation
        if cart.get("store_id") and cart["store_id"] != request.store_id:
            raise ValueError("STORE_MISMATCH")

        # 4. Catalogue Validation
        catalogue_res = await self.catalogue.validate_items(request.store_id, items)

        # 5. Eligibility Validation
        await self.eligibility.validate(
            customer_id=request.customer_id,
            store_id=request.store_id,
            items=catalogue_res["items"],
        )

        # 6. Pricing Calculation
        pricing = await self.pricing.calculate(
            catalogue_res["items"],
            request.store_id,
            request.customer_id,
        )

        # 7. Create Order Record
        order_id = str(uuid4())
        now = datetime.now(timezone.utc)
        order = {
            "id": order_id,
            "customer_id": request.customer_id,
            "store_id": request.store_id,
            "status": "RESERVING",
            "subtotal": pricing["subtotal"],
            "taxes": pricing["taxes"],
            "delivery_fee": pricing["delivery_fee"],
            "discount": pricing["discount"],
            "total": pricing["total"],
            "currency": "INR",
            "idempotency_key": request.idempotency_key,
            "created_at": now,
            "updated_at": now,
        }
        self.orders[order_id] = order

        # 8. Reserve Inventory
        try:
            for item in catalogue_res["items"]:
                await self.inventory.reserve(
                    order_id=order_id,
                    store_id=request.store_id,
                    sku_id=item["sku_id"],
                    quantity=item["quantity"],
                    idempotency_key=f"{request.idempotency_key}:{item['sku_id']}",
                )
        except Exception:
            order["status"] = "FAILED"
            raise

        # 9. PENDING_PAYMENT
        order["status"] = "PENDING_PAYMENT"
        self.idempotency_map[request.idempotency_key] = order
        return order
