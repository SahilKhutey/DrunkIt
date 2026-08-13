from pydantic import BaseModel


class WebhookPayload(BaseModel):

    event_id: str

    event_type: str

    payload: dict
