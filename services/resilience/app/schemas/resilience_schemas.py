from pydantic import BaseModel


class BackupStartRequest(BaseModel):

    resource: str = "postgresql"


class RecoveryStartRequest(BaseModel):

    service: str


class FailoverExecuteRequest(BaseModel):

    service: str

    primary: str = "region-a"

    secondary: str = "region-b"


class EmergencyActionRequest(BaseModel):

    actor: str = "sysadmin"

    reason: str = "EMERGENCY_DECLARED"
