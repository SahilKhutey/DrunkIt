from pydantic import BaseModel


class TransactionResponse(BaseModel):

    id: str

    transaction_type: str

    reference_type: str

    reference_id: str

    amount: int

    currency: str

    status: str
