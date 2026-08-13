from datetime import datetime
from pydantic import BaseModel


class ComplianceEvaluateRequest(BaseModel):

    consumer_id: str | None = None

    retailer_id: str | None = None

    rider_id: str | None = None

    product_id: str | None = None

    order_id: str | None = None

    delivery_id: str | None = None

    jurisdiction_id: str = "IN-STATE-X"

    operation: str = "CREATE_ALCOHOL_ORDER"


class ConsumerVerifyRequest(BaseModel):

    provider: str = "ID_GOV_VERIFY"


class RetailerLicenseRequest(BaseModel):

    license_number: str

    jurisdiction_id: str

    license_type: str = "EXCISE_L1"

    issuing_authority: str = "STATE_EXCISE_BOARD"


class RiderAuthorizeRequest(BaseModel):

    jurisdiction_id: str

    authorization_type: str = "REGULATED_LAST_MILE"
