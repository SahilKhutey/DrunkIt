"""Master catalog and retailer network database seed script populating premier Indian and global spirits, jurisdictions, and licensed stores."""

from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import sync_session_scope
from app.models.catalog import (
    Brand,
    Category,
    Product,
    ProductAttribute,
    ProductVariant,
    SKU,
    TasteProfile,
)
from app.models.identity import Role, User
from app.models.inventory import InventorySnapshot, Price, RetailerSKU
from app.models.retailer import Jurisdiction, Retailer, RetailerLicence, RetailerLocation


def seed_master_catalog(session: Session) -> None:
    """Populate database with master categories, premier brands, variants, SKUs, taste profiles, jurisdictions, and pilot stores."""
    # 1. Seed Roles
    for role_code in ["CONSUMER", "RETAILER", "BRAND", "ADMIN"]:
        if not session.scalars(select(Role).where(Role.code == role_code)).first():
            session.add(Role(code=role_code))
    session.flush()

    # 2. Seed Categories
    categories_data = [
        {"name": "Spirits", "slug": "spirits", "parent": None},
        {"name": "Single Malt Whisky", "slug": "single-malt-whisky", "parent": "spirits"},
        {"name": "Blended Scotch Whisky", "slug": "blended-scotch-whisky", "parent": "spirits"},
        {"name": "Craft Gin", "slug": "craft-gin", "parent": "spirits"},
        {"name": "Tequila & Agave", "slug": "tequila-agave", "parent": "spirits"},
        {"name": "Luxury Vodka", "slug": "luxury-vodka", "parent": "spirits"},
        {"name": "Dark & Spiced Rum", "slug": "rum", "parent": "spirits"},
        {"name": "RTD & Cocktails", "slug": "rtd-cocktails", "parent": None},
        {"name": "Craft Beer", "slug": "craft-beer", "parent": None},
        {"name": "No & Low Alcohol", "slug": "no-low-alcohol", "parent": None},
    ]

    cat_map: dict[str, Category] = {}
    for c_data in categories_data:
        cat = session.scalars(select(Category).where(Category.slug == c_data["slug"])).first()
        if not cat:
            parent_id = cat_map[c_data["parent"]].id if c_data["parent"] else None
            cat = Category(name=c_data["name"], slug=c_data["slug"], parent_id=parent_id)
            session.add(cat)
            session.flush()
        cat_map[c_data["slug"]] = cat

    # 3. Seed Premier Brands & Products
    brands_data = [
        {
            "name": "Indri Single Malt",
            "slug": "indri-single-malt",
            "country_code": "IN",
            "description": "Award-winning Indian single malt crafted by Piccadily Distilleries in Haryana using indigenous 6-row barley.",
            "products": [
                {
                    "name": "Indri Trini - Three Wood",
                    "slug": "indri-trini-three-wood",
                    "category": "single-malt-whisky",
                    "product_type": "WHISKY",
                    "region": "Haryana",
                    "country": "IN",
                    "abv": Decimal("46.00"),
                    "description": "Matured in Bourbon, French PX Sherry, and ex-wine casks. Notes of black tea, caramelized pineapple, and gentle oak spice.",
                    "volumes": [750, 375],
                    "prices": {750: 420000, 375: 220000},
                    "taste": {"body": Decimal("0.85"), "sweetness": Decimal("0.65"), "smokiness": Decimal("0.35"), "bitterness": Decimal("0.20"), "fruitiness": Decimal("0.80"), "spiciness": Decimal("0.70")},
                    "attributes": {"Cask Type": "Three Wood (Bourbon, PX Sherry, Red Wine)", "Barley": "Indigenous 6-Row Indian Barley", "Aging": "Sub-tropical maturation"},
                },
                {
                    "name": "Indri Diwali Collector's Edition 2024",
                    "slug": "indri-diwali-collectors-edition",
                    "category": "single-malt-whisky",
                    "product_type": "WHISKY",
                    "region": "Haryana",
                    "country": "IN",
                    "abv": Decimal("50.00"),
                    "description": "Peated single malt aged in ex-PX Sherry casks, crowned Best Single Malt in the World at Whiskies of the World Awards.",
                    "volumes": [750],
                    "prices": {750: 1200000},
                    "taste": {"body": Decimal("0.95"), "sweetness": Decimal("0.75"), "smokiness": Decimal("0.80"), "bitterness": Decimal("0.25"), "fruitiness": Decimal("0.85"), "spiciness": Decimal("0.80")},
                    "attributes": {"Cask Type": "Pedro Ximénez Sherry Cask", "Peat Level": "Moderate Peat", "Edition": "Limited Diwali Release"},
                },
            ],
        },
        {
            "name": "Amrut Single Malt",
            "slug": "amrut-single-malt",
            "country_code": "IN",
            "description": "Pioneering Indian single malt distillery in Bengaluru, Karnataka, renowned for rich tropical barrel aging.",
            "products": [
                {
                    "name": "Amrut Fusion Indian Single Malt",
                    "slug": "amrut-fusion-single-malt",
                    "category": "single-malt-whisky",
                    "product_type": "WHISKY",
                    "region": "Karnataka",
                    "country": "IN",
                    "abv": Decimal("50.00"),
                    "description": "Fusion of Scottish peated barley and unpeated Indian barley aged 3,000 feet above sea level in Bengaluru.",
                    "volumes": [750, 375],
                    "prices": {750: 540000, 375: 280000},
                    "taste": {"body": Decimal("0.90"), "sweetness": Decimal("0.55"), "smokiness": Decimal("0.75"), "bitterness": Decimal("0.30"), "fruitiness": Decimal("0.60"), "spiciness": Decimal("0.85")},
                    "attributes": {"Mash Bill": "Scottish Peated + Indian Unpeated Barley", "Altitude": "3,000 ft (Bengaluru)", "Jim Murray Score": "97/100"},
                },
            ],
        },
        {
            "name": "Glenwalk Scotch",
            "slug": "glenwalk-scotch",
            "country_code": "GB",
            "description": "Co-owned by Bollywood icon Sanjay Dutt and Cartel Bros. Premium blended Scotch whisky crafted in Scotland.",
            "products": [
                {
                    "name": "Glenwalk Blended Scotch Whisky",
                    "slug": "glenwalk-blended-scotch",
                    "category": "blended-scotch-whisky",
                    "product_type": "WHISKY",
                    "region": "Highlands",
                    "country": "GB",
                    "abv": Decimal("42.80"),
                    "description": "Meticulously blended Scotch whisky combining aged grain and malt whiskies for approachable luxury.",
                    "volumes": [750, 375, 180],
                    "prices": {750: 165000, 375: 88000, 180: 44000},
                    "taste": {"body": Decimal("0.70"), "sweetness": Decimal("0.70"), "smokiness": Decimal("0.25"), "bitterness": Decimal("0.15"), "fruitiness": Decimal("0.65"), "spiciness": Decimal("0.45")},
                    "attributes": {"Origin": "Scotland", "Partner": "Sanjay Dutt / Cartel Bros", "Style": "Smooth Blended Scotch"},
                },
            ],
        },
        {
            "name": "D'YAVOL",
            "slug": "dyavol-luxury",
            "country_code": "PL",
            "description": "Ultra-luxury lifestyle spirits brand co-founded by Shah Rukh Khan and Aryan Khan with SLIB Inc.",
            "products": [
                {
                    "name": "D'YAVOL Single Estate Luxury Vodka",
                    "slug": "dyavol-single-estate-vodka",
                    "category": "luxury-vodka",
                    "product_type": "VODKA",
                    "region": "Poland",
                    "country": "PL",
                    "abv": Decimal("40.00"),
                    "description": "Distilled in Poland from 100% select winter wheat, refined through rare black diamond charcoal filtration.",
                    "volumes": [750],
                    "prices": {750: 500000},
                    "taste": {"body": Decimal("0.65"), "sweetness": Decimal("0.30"), "smokiness": Decimal("0.05"), "bitterness": Decimal("0.10"), "fruitiness": Decimal("0.20"), "spiciness": Decimal("0.35")},
                    "attributes": {"Filtration": "Real Black Diamond Charcoal", "Grain": "100% Polish Winter Wheat", "Founders": "Shah Rukh Khan & Aryan Khan"},
                },
                {
                    "name": "D'YAVOL INCEPTION Blended Malt Scotch",
                    "slug": "dyavol-inception-scotch",
                    "category": "blended-scotch-whisky",
                    "product_type": "WHISKY",
                    "region": "Speyside & Islay",
                    "country": "GB",
                    "abv": Decimal("47.10"),
                    "description": "Peated Speyside and Islay malts finished in rare Tawny Port and Madeira wine casks.",
                    "volumes": [750],
                    "prices": {750: 950000},
                    "taste": {"body": Decimal("0.90"), "sweetness": Decimal("0.60"), "smokiness": Decimal("0.70"), "bitterness": Decimal("0.20"), "fruitiness": Decimal("0.75"), "spiciness": Decimal("0.75")},
                    "attributes": {"Casks": "Tawny Port & Madeira Finishing", "ABV": "47.1% Non-Chill Filtered"},
                },
            ],
        },
        {
            "name": "Loca Loka Tequila",
            "slug": "loca-loka-tequila",
            "country_code": "MX",
            "description": "Co-owned by superstar Rana Daggubati and Anirudh Ravichander. Authentic 100% Blue Weber Agave Tequila from Jalisco, Mexico.",
            "products": [
                {
                    "name": "Loca Loka Blanco Tequila",
                    "slug": "loca-loka-blanco",
                    "category": "tequila-agave",
                    "product_type": "TEQUILA",
                    "region": "Jalisco",
                    "country": "MX",
                    "abv": Decimal("40.00"),
                    "description": "Double-distilled pure Highland Blue Weber Agave. Clean herbal citrus notes, cooked agave, and mineral finish.",
                    "volumes": [750],
                    "prices": {750: 680000},
                    "taste": {"body": Decimal("0.75"), "sweetness": Decimal("0.50"), "smokiness": Decimal("0.20"), "bitterness": Decimal("0.20"), "fruitiness": Decimal("0.70"), "spiciness": Decimal("0.65")},
                    "attributes": {"Agave": "100% Blue Weber Highland Agave", "Distillation": "Traditional Copper Pot Stills", "Founders": "Rana Daggubati & Anirudh Ravichander"},
                },
            ],
        },
        {
            "name": "Stranger & Sons",
            "slug": "stranger-and-sons",
            "country_code": "IN",
            "description": "Globally acclaimed Indian craft gin distilled in Ponda, Goa, by Third Eye Distillery.",
            "products": [
                {
                    "name": "Stranger & Sons Indian Spirited Gin",
                    "slug": "stranger-and-sons-gin",
                    "category": "craft-gin",
                    "product_type": "GIN",
                    "region": "Goa",
                    "country": "IN",
                    "abv": Decimal("42.80"),
                    "description": "Distilled with 9 hand-picked Indian botanicals including Gondhoraj limes, black pepper, nutmeg, and mace.",
                    "volumes": [750, 375],
                    "prices": {750: 275000, 375: 145000},
                    "taste": {"body": Decimal("0.80"), "sweetness": Decimal("0.40"), "smokiness": Decimal("0.10"), "bitterness": Decimal("0.35"), "fruitiness": Decimal("0.85"), "spiciness": Decimal("0.80")},
                    "attributes": {"Key Botanical": "Gondhoraj Lime & Malabar Pepper", "Distillery": "Third Eye Distillery (Goa)"},
                },
            ],
        },
    ]

    all_skus: list[tuple[SKU, int]] = []

    for b_data in brands_data:
        brand = session.scalars(select(Brand).where(Brand.slug == b_data["slug"])).first()
        if not brand:
            brand = Brand(
                name=b_data["name"],
                slug=b_data["slug"],
                country_code=b_data["country_code"],
                description=b_data["description"],
                status="ACTIVE",
            )
            session.add(brand)
            session.flush()

        for p_data in b_data["products"]:
            product = session.scalars(select(Product).where(Product.slug == p_data["slug"])).first()
            if not product:
                cat = cat_map.get(p_data["category"])
                product = Product(
                    brand_id=brand.id,
                    category_id=cat.id if cat else None,
                    name=p_data["name"],
                    slug=p_data["slug"],
                    description=p_data["description"],
                    product_type=p_data["product_type"],
                    region=p_data["region"],
                    country_of_origin=p_data["country"],
                    abv=p_data["abv"],
                    status="ACTIVE",
                )
                session.add(product)
                session.flush()

                # Add Variants & SKUs
                for vol in p_data["volumes"]:
                    variant = ProductVariant(product_id=product.id, volume_ml=vol, packaging_type="BOTTLE")
                    session.add(variant)
                    session.flush()
                    sku_code = f"SKU_{product.slug.upper().replace('-', '_')}_{vol}"
                    sku = SKU(variant_id=variant.id, canonical_code=sku_code)
                    session.add(sku)
                    session.flush()
                    all_skus.append((sku, p_data.get("prices", {}).get(vol, 250000)))

                # Add Attributes
                for k, v in p_data["attributes"].items():
                    session.add(ProductAttribute(product_id=product.id, key=k, value=str(v)))

                # Add Taste Profile
                t = p_data["taste"]
                session.add(
                    TasteProfile(
                        product_id=product.id,
                        body=t["body"],
                        sweetness=t["sweetness"],
                        smokiness=t["smokiness"],
                        bitterness=t["bitterness"],
                        fruitiness=t["fruitiness"],
                        spiciness=t["spiciness"],
                        confidence=Decimal("1.00"),
                    )
                )

    # 4. Seed Jurisdictions
    jurisdictions_data = [
        {"country_code": "IN", "state_code": "WB", "name": "West Bengal", "timezone": "Asia/Kolkata"},
        {"country_code": "IN", "state_code": "MH", "name": "Maharashtra", "timezone": "Asia/Kolkata"},
        {"country_code": "IN", "state_code": "KA", "name": "Karnataka", "timezone": "Asia/Kolkata"},
        {"country_code": "IN", "state_code": "DL", "name": "Delhi NCT", "timezone": "Asia/Kolkata"},
        {"country_code": "IN", "state_code": "GA", "name": "Goa", "timezone": "Asia/Kolkata"},
    ]
    jur_map: dict[str, Jurisdiction] = {}
    for j_data in jurisdictions_data:
        jur = session.scalars(
            select(Jurisdiction).where(
                Jurisdiction.country_code == j_data["country_code"],
                Jurisdiction.state_code == j_data["state_code"],
            )
        ).first()
        if not jur:
            jur = Jurisdiction(
                country_code=j_data["country_code"],
                state_code=j_data["state_code"],
                name=j_data["name"],
                timezone=j_data["timezone"],
            )
            session.add(jur)
            session.flush()
        jur_map[j_data["state_code"]] = jur

    # 5. Seed Pilot Retailers & Store Locations in Kolkata (West Bengal)
    retailer = session.scalars(select(Retailer).where(Retailer.display_name == "Kolkata Spirits Co.")).first()
    if not retailer:
        retailer = Retailer(
            legal_name="Kolkata Retail Spirits & Wines Pvt Ltd",
            display_name="Kolkata Spirits Co.",
            status="ACTIVE",
            licence_status="VERIFIED",
        )
        session.add(retailer)
        session.flush()

        # Add Licence
        wb_jur = jur_map.get("WB")
        if wb_jur:
            session.add(
                RetailerLicence(
                    retailer_id=retailer.id,
                    jurisdiction_id=wb_jur.id,
                    licence_number="WB-EXC-KOL-2024-9843",
                    licence_type="OFF_TRADE_RETAIL",
                    status="ACTIVE",
                )
            )

        # Add Location: Park Street Store
        park_street = RetailerLocation(
            retailer_id=retailer.id,
            name="Park Street Premium Off-Shop",
            address="24B Park Street, Near Middleton Row",
            city="Kolkata",
            state_code="WB",
            postal_code="700016",
            country_code="IN",
            latitude=Decimal("22.551600"),
            longitude=Decimal("88.352400"),
            status="ACTIVE",
        )
        # Add Location: Salt Lake Store
        salt_lake = RetailerLocation(
            retailer_id=retailer.id,
            name="Salt Lake Sector V Cellar",
            address="Plot 5, Block DP, Salt Lake Sector V",
            city="Kolkata",
            state_code="WB",
            postal_code="700091",
            country_code="IN",
            latitude=Decimal("22.580000"),
            longitude=Decimal("88.435000"),
            status="ACTIVE",
        )
        session.add_all([park_street, salt_lake])
        session.flush()

        # Map SKUs to Store Locations and Ingest Initial Snapshots & Prices
        now = datetime.now(timezone.utc)
        for sku_obj, price_minor in all_skus:
            # Map to Park Street
            r_sku_ps = RetailerSKU(
                retailer_location_id=park_street.id,
                sku_id=sku_obj.id,
                external_sku=f"POS_PS_{sku_obj.canonical_code}",
                external_name=f"{sku_obj.canonical_code} Store Stock",
                status="ACTIVE",
            )
            # Map to Salt Lake
            r_sku_sl = RetailerSKU(
                retailer_location_id=salt_lake.id,
                sku_id=sku_obj.id,
                external_sku=f"POS_SL_{sku_obj.canonical_code}",
                external_name=f"{sku_obj.canonical_code} Sector V",
                status="ACTIVE",
            )
            session.add_all([r_sku_ps, r_sku_sl])
            session.flush()

            # Park Street Snapshot (36 units) & Price
            session.add(
                InventorySnapshot(
                    retailer_sku_id=r_sku_ps.id,
                    quantity=36,
                    availability_status="IN_STOCK",
                    source="POS_FEED",
                    captured_at=now,
                )
            )
            session.add(
                Price(
                    retailer_sku_id=r_sku_ps.id,
                    amount_minor=price_minor,
                    currency="INR",
                    effective_from=now,
                    captured_at=now,
                )
            )

            # Salt Lake Snapshot (18 units) & Price
            session.add(
                InventorySnapshot(
                    retailer_sku_id=r_sku_sl.id,
                    quantity=18,
                    availability_status="IN_STOCK",
                    source="POS_FEED",
                    captured_at=now,
                )
            )
            session.add(
                Price(
                    retailer_sku_id=r_sku_sl.id,
                    amount_minor=price_minor,
                    currency="INR",
                    effective_from=now,
                    captured_at=now,
                )
            )

    session.commit()


if __name__ == "__main__":
    with sync_session_scope() as session:
        seed_master_catalog(session)
        print("Successfully seeded master catalog & retailer network for DrunkIt v0.1.")
