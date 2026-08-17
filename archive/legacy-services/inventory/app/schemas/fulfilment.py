from pydantic import BaseModel


class FulfilmentTransition(BaseModel):

    target_status: str
