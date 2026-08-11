import datetime
import random
import uuid
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict
from .models import CreateOrderRequest, OrderResponse, OrderStatus

app = FastAPI(
    title="FACCP Order Service",
    description="Compliance-Orchestrated Order State Machine Microservice",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COMPLIANCE_SERVICE_URL = "http://localhost:8002/api/v1/compliance/evaluate"
POLICY_SERVICE_URL = "http://localhost:8008/api/v1/policies/evaluate"
AUDIT_SERVICE_URL = "http://localhost:8007/api/v1/audit/events"

ORDERS_DB: Dict[str, OrderResponse] = {}

# Pre-seed initial order
demo_order_id = "ORD-78219"
ORDERS_DB[demo_order_id] = OrderResponse(
    order_id=demo_order_id,
    consumer_id="C-1001",
    store_id="STR-BANGALORE-01",
    jurisdiction="IN-KA",
    items=[
        {
            "sku": "SKU-WHISKY-SINGLE-MALT-750",
            "product_name": "Amrut Fusion Single Malt Indian Whisky",
            "category": "SPIRITS",
            "abv": 50.0,
            "volume_ml": 750,
            "quantity": 1,
            "unit_price": 4200.0
        }
    ],
    subtotal=4200.0,
    tax=756.0,
    delivery_fee=150.0,
    platform_fee=50.0,
    total_amount=5156.0,
    status=OrderStatus.CONFIRMED,
    compliance_decision_id="DEC-88190A",
    delivery_otp="482910",
    reasons=["All regulatory compliance checks passed successfully"],
    created_at=datetime.datetime.now(datetime.timezone.utc).isoformat()
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "order-service"}

@app.post("/api/v1/orders", response_model=OrderResponse)
async def create_order(req: CreateOrderRequest):
    order_id = f"ORD-{uuid.uuid4().hex[:6].upper()}"
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

    subtotal = sum(item.unit_price * item.quantity for item in req.items)
    tax = round(subtotal * 0.18, 2)
    delivery_fee = 150.0
    platform_fee = 50.0
    total_amount = subtotal + tax + delivery_fee + platform_fee

    # 1. Call Compliance Service for Dynamic Policy Evaluation
    compliance_payload = {
        "consumer_id": req.consumer_id,
        "consumer_age_eligible": req.consumer_age_eligible,
        "store_id": req.store_id,
        "jurisdiction": req.jurisdiction,
        "license_status": "ACTIVE",
        "order_timestamp_iso": now_iso,
        "items": [
            {
                "category": item.category,
                "abv": item.abv,
                "quantity": item.quantity,
                "volume_ml": item.volume_ml
            } for item in req.items
        ]
    }

    compliance_decision_id = None
    compliance_passed = False
    reasons = []

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(COMPLIANCE_SERVICE_URL, json=compliance_payload, timeout=5.0)
            if resp.status_code == 200:
                comp_data = resp.json()
                compliance_decision_id = comp_data["decision_id"]
                reasons = comp_data["reasons"]
                compliance_passed = (comp_data["result"] == "ALLOW")
            else:
                reasons = ["Compliance evaluation service error"]
    except Exception as e:
        # Fallback local check if compliance service unreachable in standalone test
        if req.consumer_age_eligible:
            compliance_passed = True
            compliance_decision_id = f"DEC-LOCAL-{uuid.uuid4().hex[:6].upper()}"
            reasons = ["Passed local fallback compliance check"]
        else:
            reasons = ["Consumer is not age eligible"]

    if not compliance_passed:
        order_res = OrderResponse(
            order_id=order_id,
            consumer_id=req.consumer_id,
            store_id=req.store_id,
            jurisdiction=req.jurisdiction,
            items=req.items,
            subtotal=subtotal,
            tax=tax,
            delivery_fee=delivery_fee,
            platform_fee=platform_fee,
            total_amount=total_amount,
            status=OrderStatus.COMPLIANCE_BLOCKED,
            compliance_decision_id=compliance_decision_id,
            reasons=reasons,
            created_at=now_iso
        )
        ORDERS_DB[order_id] = order_res
        return order_res

    # Generate Delivery Verification OTP
    otp = f"{random.randint(100000, 999999)}"

    order_res = OrderResponse(
        order_id=order_id,
        consumer_id=req.consumer_id,
        store_id=req.store_id,
        jurisdiction=req.jurisdiction,
        items=req.items,
        subtotal=subtotal,
        tax=tax,
        delivery_fee=delivery_fee,
        platform_fee=platform_fee,
        total_amount=total_amount,
        status=OrderStatus.CONFIRMED,
        compliance_decision_id=compliance_decision_id,
        delivery_otp=otp,
        reasons=reasons,
        created_at=now_iso
    )

    ORDERS_DB[order_id] = order_res
    return order_res

@app.get("/api/v1/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: str):
    order = ORDERS_DB.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@app.get("/api/v1/orders", response_model=List[OrderResponse])
def list_orders(store_id: str = None, consumer_id: str = None):
    res = list(ORDERS_DB.values())
    if store_id:
        res = [o for o in res if o.store_id == store_id]
    if consumer_id:
        res = [o for o in res if o.consumer_id == consumer_id]
    return res

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
