from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import get_current_staff
from app.core.limiter import limiter
from app.db import models
from app.db.session import get_db
from app.domain.staff_auth.service import StaffAuthError, login
from app.schemas.schemas import StaffLoginRequest, StaffLoginResponse, StaffMeResponse

router = APIRouter(prefix="/v1/admin/auth", tags=["staff-auth"])


@router.post("/login", response_model=StaffLoginResponse)
@limiter.limit("10/minute")
def staff_login(request: Request, payload: StaffLoginRequest, db: Session = Depends(get_db)):
    try:
        session = login(db, email=payload.email, password=payload.password)
    except StaffAuthError as e:
        raise HTTPException(status_code=401, detail={"code": e.code, "message": e.message})

    staff = session.staff_user
    return StaffLoginResponse(
        access_token=session.id,
        staff_id=staff.id,
        role=staff.role.value,
        retailer_id=staff.retailer_id,
    )


@router.get("/me", response_model=StaffMeResponse)
def staff_me(staff: models.StaffUser = Depends(get_current_staff)):
    return StaffMeResponse(
        staff_id=staff.id,
        email=staff.email,
        role=staff.role.value,
        retailer_id=staff.retailer_id,
    )
