"""Brand Portal intelligence service for revenue analytics, regional distribution, and taste radar benchmarking."""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import ResourceNotFoundError
from app.models.catalog import Brand, Category, Product, ProductVariant, SKU, TasteProfile
from app.models.commerce import Order, OrderItem
from app.models.inventory import InventorySnapshot, RetailerSKU
from app.models.retailer import Jurisdiction, RetailerLocation
from app.schemas.brand_portal import (
    BrandDashboardResponse,
    BrandRegionalDistribution,
    BrandSKUMarketShare,
    BrandTasteRadarVisualization,
)


def _format_inr(amount_minor: int) -> str:
    """Format minor currency units (paise) into INR string."""
    rupees = amount_minor / 100.0
    return f"₹{rupees:,.2f}"


class BrandPortalService:
    """Service handling brand house intelligence, radar analytics, and regional stockist tracking."""

    @classmethod
    def get_brand_dashboard(cls, brand_id: uuid.UUID, session: Session) -> BrandDashboardResponse:
        """Compute holistic commercial performance, market share, and taste radar intelligence for a brand."""
        brand = session.scalars(
            select(Brand)
            .where(Brand.id == brand_id)
            .options(
                selectinload(Brand.products)
                .selectinload(Product.variants)
                .selectinload(ProductVariant.skus),
                selectinload(Brand.products).selectinload(Product.taste_profile),
                selectinload(Brand.products).selectinload(Product.category),
            )
        ).first()

        if not brand:
            raise ResourceNotFoundError(f"Brand '{brand_id}' was not found.")

        # 1. Gather all SKUs under this Brand
        brand_skus: list[SKU] = []
        sku_to_product: dict[uuid.UUID, Product] = {}
        for prod in brand.products:
            for var in prod.variants:
                for sku in var.skus:
                    brand_skus.append(sku)
                    sku_to_product[sku.id] = prod

        brand_sku_ids = [s.id for s in brand_skus]

        # 2. Query Orders & Revenue Performance
        order_items = []
        if brand_sku_ids:
            order_items = list(
                session.scalars(
                    select(OrderItem)
                    .where(OrderItem.sku_id.in_(brand_sku_ids))
                    .options(selectinload(OrderItem.order))
                ).all()
            )

        sku_performance: dict[uuid.UUID, dict[str, Any]] = {
            sku.id: {
                "sku_id": sku.id,
                "sku_code": sku.canonical_code,
                "product_name": sku_to_product[sku.id].name if sku.id in sku_to_product else "Spirit",
                "volume_ml": sku.variant.volume_ml if sku.variant else 750,
                "orders_count": 0,
                "units_sold": 0,
                "gross_revenue_minor": 0,
            }
            for sku in brand_skus
        }

        total_orders_set = set()
        total_revenue_minor = 0

        for item in order_items:
            if item.order and item.order.status != "CANCELLED":
                perf = sku_performance[item.sku_id]
                perf["units_sold"] += item.quantity
                perf["orders_count"] += 1
                perf["gross_revenue_minor"] += item.unit_price_minor * item.quantity
                total_revenue_minor += item.unit_price_minor * item.quantity
                total_orders_set.add(item.order_id)

        top_skus = [
            BrandSKUMarketShare(
                sku_id=p["sku_id"],
                sku_code=p["sku_code"],
                product_name=p["product_name"],
                volume_ml=p["volume_ml"],
                orders_count=p["orders_count"],
                units_sold=p["units_sold"],
                gross_revenue_minor=p["gross_revenue_minor"],
                gross_revenue_formatted=_format_inr(p["gross_revenue_minor"]),
            )
            for p in sku_performance.values()
        ]
        top_skus.sort(key=lambda s: s.gross_revenue_minor, reverse=True)

        # 3. Stockist Density & Regional Distribution
        ret_skus = []
        if brand_sku_ids:
            ret_skus = list(
                session.scalars(
                    select(RetailerSKU)
                    .where(RetailerSKU.sku_id.in_(brand_sku_ids))
                    .options(
                        selectinload(RetailerSKU.location),
                        selectinload(RetailerSKU.snapshots),
                    )
                ).all()
            )

        unique_locations = {r.retailer_location_id for r in ret_skus}

        # Group by State Code
        regional_map: dict[str, dict[str, Any]] = {}
        for r in ret_skus:
            if not r.location:
                continue
            state = f"IN-{r.location.state_code}"
            if state not in regional_map:
                regional_map[state] = {
                    "state_code": state,
                    "state_name": r.location.city or state,
                    "locations": set(),
                    "retailers": set(),
                    "total_snapshots": 0,
                    "in_stock_snapshots": 0,
                    "volume_sold_litres": 0.0,
                }
            reg = regional_map[state]
            reg["locations"].add(r.retailer_location_id)
            reg["retailers"].add(r.location.retailer_id)

            if r.snapshots:
                latest = max(
                    r.snapshots,
                    key=lambda s: s.captured_at if s.captured_at.tzinfo else s.captured_at.replace(tzinfo=timezone.utc),
                )
                reg["total_snapshots"] += 1
                if latest.availability_status == "IN_STOCK":
                    reg["in_stock_snapshots"] += 1

        # Calculate volume sold per state
        for item in order_items:
            if item.order and item.order.location:
                st = f"IN-{item.order.location.state_code}"
                if st in regional_map:
                    vol_l = (item.sku.variant.volume_ml if item.sku and item.sku.variant else 750) * item.quantity / 1000.0
                    regional_map[st]["volume_sold_litres"] += vol_l

        regional_distribution = [
            BrandRegionalDistribution(
                state_code=reg["state_code"],
                state_name=reg["state_name"],
                active_retailers_count=len(reg["retailers"]),
                active_locations_count=len(reg["locations"]),
                in_stock_ratio=round(reg["in_stock_snapshots"] / max(1, reg["total_snapshots"]), 2),
                volume_sold_litres=round(reg["volume_sold_litres"], 2),
            )
            for reg in regional_map.values()
        ]

        # 4. Taste Radar Visualizations with Peer Benchmarks
        taste_radars = cls.get_brand_taste_radars(brand_id, session)

        return BrandDashboardResponse(
            brand_id=brand.id,
            brand_name=brand.name,
            brand_slug=brand.slug,
            total_products=len(brand.products),
            total_skus=len(brand_skus),
            total_licensed_stockists=len(unique_locations),
            total_orders=len(total_orders_set),
            total_gross_revenue_minor=total_revenue_minor,
            total_gross_revenue_formatted=_format_inr(total_revenue_minor),
            top_performing_skus=top_skus,
            regional_distribution=regional_distribution,
            taste_radars=taste_radars,
        )

    @classmethod
    def get_brand_taste_radars(
        cls,
        brand_id: uuid.UUID,
        session: Session,
    ) -> list[BrandTasteRadarVisualization]:
        """Generate 6-axis taste radar profiles with peer category benchmark averages."""
        brand = session.scalars(
            select(Brand)
            .where(Brand.id == brand_id)
            .options(
                selectinload(Brand.products).selectinload(Product.taste_profile),
                selectinload(Brand.products).selectinload(Product.category),
            )
        ).first()

        if not brand:
            raise ResourceNotFoundError(f"Brand '{brand_id}' was not found.")

        # Precompute category benchmarks
        all_profiles = list(
            session.scalars(
                select(TasteProfile)
                .join(Product, TasteProfile.product_id == Product.id)
                .options(selectinload(TasteProfile.product))
            ).all()
        )

        category_benchmarks: dict[str, dict[str, float]] = {}
        for tp in all_profiles:
            if not tp.product or not tp.product.category_id:
                continue
            cat_id_str = str(tp.product.category_id)
            if cat_id_str not in category_benchmarks:
                category_benchmarks[cat_id_str] = {
                    "count": 0,
                    "body": 0.0,
                    "sweetness": 0.0,
                    "smokiness": 0.0,
                    "bitterness": 0.0,
                    "fruitiness": 0.0,
                    "spiciness": 0.0,
                }
            bm = category_benchmarks[cat_id_str]
            bm["count"] += 1
            bm["body"] += float(tp.body or 0.5)
            bm["sweetness"] += float(tp.sweetness or 0.5)
            bm["smokiness"] += float(tp.smokiness or 0.5)
            bm["bitterness"] += float(tp.bitterness or 0.5)
            bm["fruitiness"] += float(tp.fruitiness or 0.5)
            bm["spiciness"] += float(tp.spiciness or 0.5)

        radar_visualizations: list[BrandTasteRadarVisualization] = []

        for prod in brand.products:
            tp = prod.taste_profile
            axes = {
                "body": float(tp.body or 0.5) if tp else 0.5,
                "sweetness": float(tp.sweetness or 0.5) if tp else 0.5,
                "smokiness": float(tp.smokiness or 0.5) if tp else 0.5,
                "bitterness": float(tp.bitterness or 0.5) if tp else 0.5,
                "fruitiness": float(tp.fruitiness or 0.5) if tp else 0.5,
                "spiciness": float(tp.spiciness or 0.5) if tp else 0.5,
            }

            # Peer category average
            cat_id_str = str(prod.category_id) if prod.category_id else None
            if cat_id_str and cat_id_str in category_benchmarks:
                bm = category_benchmarks[cat_id_str]
                cnt = max(1, bm["count"])
                benchmark = {
                    "body": round(bm["body"] / cnt, 2),
                    "sweetness": round(bm["sweetness"] / cnt, 2),
                    "smokiness": round(bm["smokiness"] / cnt, 2),
                    "bitterness": round(bm["bitterness"] / cnt, 2),
                    "fruitiness": round(bm["fruitiness"] / cnt, 2),
                    "spiciness": round(bm["spiciness"] / cnt, 2),
                }
            else:
                benchmark = {
                    "body": 0.65,
                    "sweetness": 0.50,
                    "smokiness": 0.35,
                    "bitterness": 0.25,
                    "fruitiness": 0.60,
                    "spiciness": 0.55,
                }

            # Generate flavor tags
            tags = []
            if axes["smokiness"] >= 0.6:
                tags.append("Peated")
            if axes["body"] >= 0.8:
                tags.append("Full Bodied")
            if axes["fruitiness"] >= 0.7:
                tags.append("Fruity & Floral")
            if axes["spiciness"] >= 0.7:
                tags.append("Botanical Spice")
            if axes["sweetness"] >= 0.6:
                tags.append("Sweet Malt")

            radar_visualizations.append(
                BrandTasteRadarVisualization(
                    product_id=prod.id,
                    product_name=prod.name,
                    product_slug=prod.slug,
                    radar_axes=axes,
                    category_benchmark=benchmark,
                    flavor_tags=tags,
                )
            )

        return radar_visualizations
