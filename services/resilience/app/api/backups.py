from fastapi import APIRouter, HTTPException
from services.resilience.app.schemas.resilience_schemas import BackupStartRequest
from services.resilience.app.services.backup_service import BackupService

router = APIRouter(
    prefix="/api/v1/backups",
    tags=["Backups"],
)

backup_service = BackupService()


@router.post("/start")
async def start_backup(payload: BackupStartRequest):
    return await backup_service.start_backup(resource=payload.resource)


@router.get("")
async def list_backups():
    return await backup_service.list_backups()


@router.get("/{backup_id}")
async def get_backup(backup_id: str):
    b = await backup_service.get_backup(backup_id)
    if not b:
        raise HTTPException(status_code=404, detail="BACKUP_NOT_FOUND")
    return b


@router.post("/{backup_id}/verify")
async def verify_backup(backup_id: str):
    try:
        return await backup_service.verify_backup_record(backup_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
