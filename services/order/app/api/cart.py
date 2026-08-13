from fastapi import APIRouter, HTTPException
from services.order.app.schemas.cart import CartItemAdd, CartItemUpdate
from services.order.app.services.cart_service import CartService

router = APIRouter(
    prefix="/cart",
    tags=["Cart"],
)

cart_service = CartService()


@router.post("/{cart_id}/items")
async def add_item(
    cart_id: str,
    payload: CartItemAdd,
):
    if payload.quantity <= 0:
        raise HTTPException(status_code=400, detail="INVALID_QUANTITY")
    return await cart_service.add_item(cart_id, payload.sku_id, payload.quantity)


@router.patch("/{cart_id}/items/{sku_id}")
async def update_item(
    cart_id: str,
    sku_id: str,
    payload: CartItemUpdate,
):
    try:
        return await cart_service.update_item(cart_id, sku_id, payload.quantity)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
