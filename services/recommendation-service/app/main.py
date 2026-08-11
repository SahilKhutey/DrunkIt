from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app
from pydantic import BaseModel

from faccp_common.dto import APIResponse
from faccp_common.middleware import register_exception_handlers, register_middleware
from app.config import get_settings
from app.services.recommender import ProductRecommender

settings = get_settings()
recommender = ProductRecommender()


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    # Seed mock products for recommendation testing
    recommender.set_product_attributes("p1", {"name": "Single Malt Scotch 12Y", "category": "spirit", "brand": "Glen", "abv": 40})
    recommender.set_product_attributes("p2", {"name": "Craft IPA Beer", "category": "beer", "brand": "Bira", "abv": 5})
    recommender.set_product_attributes("p3", {"name": "Cabernet Sauvignon", "category": "wine", "brand": "Sula", "abv": 13})
    recommender.record_interaction("user1", "p1", "purchase")
    recommender.record_interaction("user1", "p3", "view")
    yield


class RecommendRequest(BaseModel):
    user_id: str
    n: int = 10
    context: dict[str, Any] | None = None


def create_app() -> FastAPI:
    app = FastAPI(title="FACCP Recommendation Service", version=settings.service_version, lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    register_middleware(app)
    register_exception_handlers(app)
    app.mount("/metrics", make_asgi_app())

    @app.get("/health")
    async def health():
        return {"status": "ok", "service": settings.service_name}

    @app.post("/api/v1/recommendations")
    async def get_recommendations(payload: RecommendRequest) -> APIResponse[list[dict]]:
        results = recommender.recommend(payload.user_id, n=payload.n, context=payload.context)
        return APIResponse(data=results)

    return app


app = create_app()
