# FACCP Catalog Service

Canonical Product Master, Categories, Brands, SKUs, and Store Listings.

## Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | /api/v1/catalog/categories | Admin | Create category |
| GET | /api/v1/catalog/categories | Public | List categories |
| POST | /api/v1/catalog/brands | Admin | Create brand |
| GET | /api/v1/catalog/brands | Public | List brands |
| POST | /api/v1/catalog/products | Admin | Create Product Master |
| GET | /api/v1/catalog/products/{id} | Public | Get product details |
| GET | /api/v1/catalog/products | Public | List active products |
| POST | /api/v1/catalog/store-listings | Retailer | Create store listing |
| GET | /api/v1/catalog/store-listings/{store_id} | Public | List store listings |

## Development

```bash
# Run migrations
uv run alembic upgrade head

# Seed catalog
uv run python -m app.scripts.seed_catalog

# Start service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
```
