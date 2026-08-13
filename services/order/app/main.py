from fastapi import FastAPI
from services.order.app.api.cancellations import router as cancellations_router
from services.order.app.api.cart import router as cart_router
from services.order.app.api.checkout import router as checkout_router
from services.order.app.api.orders import router as orders_router

app = FastAPI(
    title="Order Management & Checkout Core Service",
    version="1.0.0",
)

app.include_router(cart_router)
app.include_router(checkout_router)
app.include_router(orders_router)
app.include_router(cancellations_router)


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "order"}
