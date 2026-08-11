"""
Double-entry financial ledger.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from faccp_common.exceptions import ValidationError
from faccp_common.logging import get_logger

from app.db.models import LedgerEntry

logger = get_logger(__name__)


class LedgerService:

    CONSUMER_PAYABLE = "consumer_payable"
    RETAILER_RECEIVABLE = "retailer_receivable"
    DELIVERY_RECEIVABLE = "delivery_receivable"
    PLATFORM_REVENUE = "platform_revenue"
    TAX_PAYABLE = "tax_payable"
    PROCESSOR_CLEARING = "payment_processor_clearing"
    CASH = "cash"

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def post_double_entry(
        self,
        *,
        description: str,
        debit_account: str,
        credit_account: str,
        amount: Decimal,
        currency: str = "INR",
        debit_holder_id: str | None = None,
        credit_holder_id: str | None = None,
        transaction_id: str | None = None,
        refund_id: str | None = None,
        correlation_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[LedgerEntry, LedgerEntry]:
        if amount <= 0:
            raise ValidationError("Amount must be positive", details={"amount": str(amount)})
        now = datetime.now(timezone.utc)
        entry_number_debit = self._new_entry_number()
        entry_number_credit = self._new_entry_number()

        debit = LedgerEntry(
            id=str(uuid.uuid4()),
            entry_number=entry_number_debit,
            transaction_id=transaction_id,
            refund_id=refund_id,
            account_type=debit_account,
            account_holder_id=debit_holder_id,
            debit=amount,
            credit=Decimal("0"),
            currency=currency,
            description=description,
            correlation_id=correlation_id,
            posted_at=now,
            metadata_json=metadata or {},
        )
        credit = LedgerEntry(
            id=str(uuid.uuid4()),
            entry_number=entry_number_credit,
            transaction_id=transaction_id,
            refund_id=refund_id,
            account_type=credit_account,
            account_holder_id=credit_holder_id,
            debit=Decimal("0"),
            credit=amount,
            currency=currency,
            description=description,
            correlation_id=correlation_id,
            posted_at=now,
            metadata_json=metadata or {},
        )
        self.db.add_all([debit, credit])
        await self.db.flush()
        logger.info(
            "ledger.entry.posted",
            entry_number=entry_number_debit,
            amount=str(amount),
            currency=currency,
            debit_account=debit_account,
            credit_account=credit_account,
        )
        return debit, credit

    async def get_account_balance(
        self, account_type: str, account_holder_id: str | None = None, currency: str = "INR"
    ) -> Decimal:
        from sqlalchemy import select, func
        q = select(
            func.coalesce(func.sum(LedgerEntry.debit), 0).label("total_debit"),
            func.coalesce(func.sum(LedgerEntry.credit), 0).label("total_credit"),
        ).where(
            LedgerEntry.account_type == account_type,
            LedgerEntry.currency == currency,
        )
        if account_holder_id:
            q = q.where(LedgerEntry.account_holder_id == account_holder_id)
        result = await self.db.execute(q)
        row = result.one()
        return Decimal(str(row.total_debit)) - Decimal(str(row.total_credit))

    def _new_entry_number(self) -> str:
        return f"LED-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
