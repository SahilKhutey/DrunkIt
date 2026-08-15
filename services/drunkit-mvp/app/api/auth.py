from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.domain.auth.service import AuthError, request_otp, verify_otp
from app.schemas.schemas import OTPRequestRequest, OTPRequestResponse, OTPVerifyRequest, OTPVerifyResponse

router = APIRouter(prefix="/v1/auth", tags=["auth"])


@router.post("/otp/request", response_model=OTPRequestResponse)
def request_otp_endpoint(payload: OTPRequestRequest, db: Session = Depends(get_db)):
    try:
        request_id, expires_in, dev_otp = request_otp(db, phone=payload.phone)
    except AuthError as e:
        # COOLDOWN_ACTIVE is a rate-limit-class error: 429 is semantically
        # correct ("too many requests for this phone"). All other AuthErrors
        # at the request stage are 422.
        status = 429 if e.code == "COOLDOWN_ACTIVE" else 422
        raise HTTPException(status_code=status, detail={"code": e.code, "message": e.message})
    return OTPRequestResponse(request_id=request_id, expires_in_seconds=expires_in, dev_otp=dev_otp)


@router.post("/otp/verify", response_model=OTPVerifyResponse)
def verify_otp_endpoint(payload: OTPVerifyRequest, db: Session = Depends(get_db)):
    try:
        session = verify_otp(db, phone=payload.phone, code=payload.code)
    except AuthError as e:
        raise HTTPException(status_code=422, detail={"code": e.code, "message": e.message})
    return OTPVerifyResponse(access_token=session.id, consumer_id=session.consumer_id)

