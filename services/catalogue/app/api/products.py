from fastapi import APIRouter
from services.catalogue.app.schemas.product import ProductCreate
from services.catalogue.app.services.product_service import ProductService

router = APIRouter(
    prefix="/admin/products",
    tags=["Admin Products"],
)

product_service = ProductService()


@router.post("")
async def create_product(payload: ProductCreate):
    return await product_service.create(payload)
