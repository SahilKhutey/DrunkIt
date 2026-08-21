"""Consumer discovery service managing occasion collections, spotlight feeds, and semantic taste vector similarity matching."""

import math
import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.catalog import Brand, Product, TasteProfile
from app.schemas.catalog import (
    BrandResponse,
    ProductSummaryResponse,
    TasteProfileSchema,
)
from app.schemas.discovery import (
    DiscoveryFeedResponse,
    OccasionCollection,
    TasteMatchQuery,
    TasteMatchResult,
)


def _product_to_summary(p: Product) -> ProductSummaryResponse:
    """Format a Product model into ProductSummaryResponse."""
    return ProductSummaryResponse(
        id=p.id,
        brand_id=p.brand_id,
        brand_name=p.brand.name if p.brand else None,
        category_id=p.category_id,
        category_name=p.category.name if p.category else None,
        name=p.name,
        slug=p.slug,
        product_type=p.product_type,
        region=p.region,
        country_of_origin=p.country_of_origin,
        abv=p.abv,
        status=p.status,
        created_at=p.created_at,
    )


def _compute_cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Calculate cosine similarity between two taste profile vectors."""
    dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
    magnitude_a = math.sqrt(sum(a * a for a in vec_a))
    magnitude_b = math.sqrt(sum(b * b for b in vec_b))

    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0
    similarity = dot_product / (magnitude_a * magnitude_b)
    return round(max(0.0, min(1.0, similarity)), 4)


def _generate_match_reasons(
    query_vals: dict[str, float], product_vals: dict[str, float]
) -> list[str]:
    """Generate human-readable explanations for why this spirit was matched."""
    reasons = []
    dimension_labels = {
        "smokiness": "peat and smoke",
        "body": "rich mouthfeel and body",
        "fruitiness": "vibrant fruit notes",
        "sweetness": "sweet malt/caramel profile",
        "spiciness": "botanical and cask spice",
        "bitterness": "clean botanical finish",
    }

    for dim, label in dimension_labels.items():
        q = query_vals.get(dim, 0.5)
        p = product_vals.get(dim, 0.5)
        # If user prioritized this dimension (> 0.6) and product delivers strongly (abs diff <= 0.25)
        if q >= 0.6 and p >= 0.6:
            reasons.append(f"Delivers intense {label} ({p:.2f}) aligned with your preference")
        elif q <= 0.3 and p <= 0.3:
            reasons.append(f"Low {label} as requested")

    if not reasons:
        reasons.append("Balanced flavor profile aligning with your radar selections")
    return reasons[:3]


class DiscoveryService:
    """Service handling consumer discovery feeds, occasions, and flavor radar matching."""

    # 1. Occasion Collections
    @classmethod
    def get_occasions(cls, session: Session) -> list[OccasionCollection]:
        """Generate structured occasion collections dynamically from master catalog."""
        products = list(
            session.scalars(
                select(Product)
                .options(
                    selectinload(Product.brand),
                    selectinload(Product.category),
                    selectinload(Product.taste_profile),
                )
                .where(Product.status == "ACTIVE")
            ).all()
        )

        # 1. Peat & Smoke Collection (Smokiness >= 0.5)
        peat_products = [
            _product_to_summary(p)
            for p in products
            if p.taste_profile and float(p.taste_profile.smokiness or 0) >= 0.5
        ]

        # 2. Craft & Indigenous Explorers (Gin, Tequila, Indian Single Malts)
        craft_products = [
            _product_to_summary(p)
            for p in products
            if p.product_type in ["GIN", "TEQUILA"] or p.country_of_origin == "IN"
        ]

        # 3. Smooth & Approachable (Sweetness >= 0.5, Bitterness <= 0.25)
        smooth_products = [
            _product_to_summary(p)
            for p in products
            if p.taste_profile
            and float(p.taste_profile.sweetness or 0) >= 0.5
            and float(p.taste_profile.bitterness or 0) <= 0.25
        ]

        # 4. Celebration & Gifting (ABV >= 45% or single malts / luxury vodka)
        gifting_products = [
            _product_to_summary(p)
            for p in products
            if (p.abv and float(p.abv) >= 46.0) or p.product_type == "VODKA"
        ]

        # 5. High Proof Specialists (ABV >= 46%)
        high_proof_products = [
            _product_to_summary(p)
            for p in products
            if p.abv and float(p.abv) >= 46.0
        ]

        collections = [
            OccasionCollection(
                slug="celebration-gift",
                title="Celebration & Gifting",
                subtitle="World-class collector's editions and luxury prestige expressions.",
                hero_tag="PREMIUM",
                item_count=len(gifting_products),
                items=gifting_products,
            ),
            OccasionCollection(
                slug="peat-and-smoke",
                title="Peat & Smoke Aficionados",
                subtitle="Heavy peated single malts, Islay blends, and bold smoky profiles.",
                hero_tag="BOLD",
                item_count=len(peat_products),
                items=peat_products,
            ),
            OccasionCollection(
                slug="craft-indie-explorers",
                title="Indian Craft & Indie Explorers",
                subtitle="Rare Indian botanicals, craft agave, and independent distilleries.",
                hero_tag="CRAFT",
                item_count=len(craft_products),
                items=craft_products,
            ),
            OccasionCollection(
                slug="smooth-and-approachable",
                title="Smooth & Approachable Sippers",
                subtitle="Silky malts, smooth agave, and balanced spirits for relaxed evenings.",
                hero_tag="EASY_SIPPER",
                item_count=len(smooth_products),
                items=smooth_products,
            ),
            OccasionCollection(
                slug="high-proof-specialists",
                title="High-Proof & Cask Strength",
                subtitle="Full-intensity spirits bottled at 46% ABV and above for rich flavor.",
                hero_tag="HIGH_PROOF",
                item_count=len(high_proof_products),
                items=high_proof_products,
            ),
        ]
        return collections

    @classmethod
    def get_occasion_by_slug(cls, slug: str, session: Session) -> OccasionCollection | None:
        """Retrieve a specific occasion collection by slug."""
        occasions = cls.get_occasions(session)
        for oc in occasions:
            if oc.slug == slug:
                return oc
        return None

    # 2. Semantic Taste Matching Engine
    @classmethod
    def match_taste_profile(cls, query: TasteMatchQuery, session: Session) -> list[TasteMatchResult]:
        """Perform cosine vector similarity matching across 6 flavor radar dimensions."""
        stmt = (
            select(Product)
            .join(TasteProfile, Product.id == TasteProfile.product_id)
            .options(
                selectinload(Product.brand),
                selectinload(Product.category),
                selectinload(Product.taste_profile),
            )
            .where(Product.status == "ACTIVE")
        )

        if query.preferred_types:
            stmt = stmt.where(Product.product_type.in_([t.upper() for t in query.preferred_types]))
        if query.min_abv is not None:
            stmt = stmt.where(Product.abv >= query.min_abv)
        if query.max_abv is not None:
            stmt = stmt.where(Product.abv <= query.max_abv)

        products = list(session.scalars(stmt).all())

        # Construct Query Vector (defaulting missing dimensions to 0.5 neutral)
        query_dict = {
            "body": float(query.body) if query.body is not None else 0.5,
            "sweetness": float(query.sweetness) if query.sweetness is not None else 0.5,
            "smokiness": float(query.smokiness) if query.smokiness is not None else 0.5,
            "bitterness": float(query.bitterness) if query.bitterness is not None else 0.5,
            "fruitiness": float(query.fruitiness) if query.fruitiness is not None else 0.5,
            "spiciness": float(query.spiciness) if query.spiciness is not None else 0.5,
        }
        query_vec = [
            query_dict["body"],
            query_dict["sweetness"],
            query_dict["smokiness"],
            query_dict["bitterness"],
            query_dict["fruitiness"],
            query_dict["spiciness"],
        ]

        scored_results: list[TasteMatchResult] = []

        for p in products:
            tp = p.taste_profile
            if not tp:
                continue

            prod_dict = {
                "body": float(tp.body or 0.5),
                "sweetness": float(tp.sweetness or 0.5),
                "smokiness": float(tp.smokiness or 0.5),
                "bitterness": float(tp.bitterness or 0.5),
                "fruitiness": float(tp.fruitiness or 0.5),
                "spiciness": float(tp.spiciness or 0.5),
            }
            prod_vec = [
                prod_dict["body"],
                prod_dict["sweetness"],
                prod_dict["smokiness"],
                prod_dict["bitterness"],
                prod_dict["fruitiness"],
                prod_dict["spiciness"],
            ]

            similarity = _compute_cosine_similarity(query_vec, prod_vec)
            reasons = _generate_match_reasons(query_dict, prod_dict)

            scored_results.append(
                TasteMatchResult(
                    product=_product_to_summary(p),
                    similarity_score=similarity,
                    match_reasons=reasons,
                    taste_profile=TasteProfileSchema.model_validate(tp),
                )
            )

        # Sort descending by similarity score
        scored_results.sort(key=lambda r: r.similarity_score, reverse=True)
        return scored_results[: query.limit]

    # 3. Discovery Feed Aggregator
    @classmethod
    def get_discovery_feed(cls, session: Session) -> DiscoveryFeedResponse:
        """Compose the main consumer discovery feed."""
        brands = list(
            session.scalars(
                select(Brand)
                .where(Brand.status == "ACTIVE")
                .order_by(Brand.name.asc())
                .limit(10)
            ).all()
        )
        brand_responses = [BrandResponse.model_validate(b) for b in brands]
        occasions = cls.get_occasions(session)

        # Spotlight products: Top 5 spirits
        spotlight = list(
            session.scalars(
                select(Product)
                .options(selectinload(Product.brand), selectinload(Product.category))
                .where(Product.status == "ACTIVE")
                .order_by(Product.name.asc())
                .limit(5)
            ).all()
        )
        spotlight_summaries = [_product_to_summary(p) for p in spotlight]

        return DiscoveryFeedResponse(
            featured_brands=brand_responses,
            occasions=occasions,
            spotlight_products=spotlight_summaries,
        )
