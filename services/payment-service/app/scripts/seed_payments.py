"""Seed sample payment intents and ledger entries."""

from __future__ import annotations

import asyncio
from sqlalchemy import select

from app.config import get_settings
from app.db.base import Base
from app.db.models import DoubleEntryLedger, PaymentIntent, PaymentTransaction
from faccp_common.database import init_engine, session_scope

SAMPLE_INTENTS = [
    {
        "order_id": "ORD_SEED_001",
        "consumer_id": "usr_consumer_seed_101",
        "amount_inr": 2850.0,
        "status": "CAPTURED",
        "gateway_provider": "STUB_PAY",
        "gateway_transaction_id": "TXN_STUB_20260812_001",
    }
]


async def seed() -> None:
    settings = get_settings()
    init_engine(settings.database_url)
    async with session_scope() as session:
        for p in SAMPLE_INTENTS:
            existing = await session.execute(
                select(PaymentIntent).where(PaymentIntent.order_id == p["order_id"])
            )
            if existing.scalar_one_or_none() is None:
                intent = PaymentIntent(
                    order_id=p["order_id"],
                    consumer_id=p["consumer_id"],
                    amount_inr=p["amount_inr"],
                    currency="INR",
                    status=p["status"],
                    gateway_provider=p["gateway_provider"],
                    gateway_transaction_id=p["gateway_transaction_id"],
                )
                session.add(intent)
                await session.flush()

                tx = PaymentTransaction(
                    intent_id=intent.id,
                    transaction_type="CAPTURE",
                    amount_inr=p["amount_inr"],
                    status="SUCCESS",
                )
                session.add(tx)

                ledger = DoubleEntryLedger(
                    entry_id="ENT_SEED_001",
                    account_debit="CONSUMER_ESCROW",
                    account_credit="RETAILER_PAYABLE",
                    amount_inr=p["amount_inr"],
                    reference_id=p["order_id"],
                )
                session.add(ledger)
                print(f"  Payment intent seeded: Order {p['order_id']} ({p['amount_inr']} INR)")

    print("\n[OK] Seeded payment intents and double-entry ledger.")


if __name__ == "__main__":
    asyncio.run(seed())
