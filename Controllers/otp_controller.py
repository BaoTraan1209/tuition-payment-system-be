from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from Security.auth_dependency import get_current_user

from config.db import get_db
from Services.otp_service import (
    request_otp,
    verify_otp
)

router = APIRouter(
    prefix="/otps",
    tags=["Otps"]
)


class OtpRequest(BaseModel):
    payment_id: int = Field(gt=0)


class OtpVerification(BaseModel):
    payment_id: int = Field(gt=0)
    otp: str = Field(
        min_length=6,
        max_length=6,
        pattern=r"^[0-9]{6}$"
    )


@router.post("/request")
def request_otp_endpoint(
    data: OtpRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        result = request_otp(db, data.payment_id, int(current_user.payer_id))

        return {
            "success": True,
            "message": "OTP sent successfully.",
            "data": result
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


@router.post("/verify")
def verify_otp_endpoint(
    data: OtpVerification,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        verify_otp(
            db,
            data.payment_id,
            data.otp,
            int(current_user.payer_id)
        )

        return {
            "success": True,
            "message": "OTP verified successfully."
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
