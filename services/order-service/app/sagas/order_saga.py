"""
Order processing saga.
Steps:
1. Reserve inventory
2. Authorize payment
3. Create delivery task
4. Confirm order
Compensations (in reverse):
1. Cancel delivery
2. Void payment authorization
3. Release inventory reservation
"""

from faccp_common.saga import Saga, SagaStep, CompensationAction
from faccp_common.saga.orchestrator import SagaOrchestrator
from faccp_common.logging import get_logger

logger = get_logger(__name__)


def build_order_saga(
    order_id: str,
    store_id: str,
    consumer_id: str,
    items: list[dict],
    payment_intent_id: str,
    delivery_address: dict,
    reserve_inventory_fn,
    authorize_payment_fn,
    create_delivery_fn,
    cancel_delivery_fn,
    void_payment_fn,
    release_inventory_fn,
) -> Saga:
    """Build the order processing saga."""
    saga = Saga(
        name=f"process_order:{order_id}",
        context={
            "order_id": order_id,
            "store_id": store_id,
            "consumer_id": consumer_id,
            "items": items,
            "payment_intent_id": payment_intent_id,
            "delivery_address": delivery_address,
        },
        steps=[
            SagaStep(
                name="reserve_inventory",
                action=lambda ctx: reserve_inventory_fn(
                    order_id=ctx["order_id"],
                    store_id=ctx["store_id"],
                    items=ctx["items"],
                ),
                compensation=CompensationAction(
                    name="release_inventory",
                    func=release_inventory_fn,
                    args={"order_id": order_id},
                ),
            ),
            SagaStep(
                name="authorize_payment",
                action=lambda ctx: authorize_payment_fn(
                    intent_id=ctx["payment_intent_id"],
                ),
                compensation=CompensationAction(
                    name="void_payment",
                    func=void_payment_fn,
                    args={"intent_id": payment_intent_id},
                ),
            ),
            SagaStep(
                name="create_delivery",
                action=lambda ctx: create_delivery_fn(
                    order_id=ctx["order_id"],
                    address=ctx["delivery_address"],
                ),
                compensation=CompensationAction(
                    name="cancel_delivery",
                    func=cancel_delivery_fn,
                    args={"order_id": order_id},
                ),
            ),
            SagaStep(
                name="confirm_order",
                action=lambda ctx: {"confirmed": True, "order_id": ctx["order_id"]},
            ),
        ],
    )
    return saga
