from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from config.db import get_db
from Security.auth_dependency import get_current_user
from Services.payment_otp_service import PaymentOTPService
from Models.user import User
from Helpers.response_helper import send_success_response

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payment/otp", tags=["Payment OTP"])

otp_service = PaymentOTPService()

class VerifyOTPRequest(BaseModel):
    tuition_fee_id: int = Field(gt=0)
    otp: str = Field(pattern=r"^\d{6}$")

@router.post("/send")
def send_payment_otp(
    tuition_fee_id: int = Query(gt=0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user = db.query(User).filter(
        User.id == current_user.id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if not user.email:
        raise HTTPException(status_code=400, detail="User email not found.")

    try:
        result = otp_service.send_otp(
            str(current_user.id),
            tuition_fee_id,
            user.email
        )

        return send_success_response(
            data={
                "expires_in": result["expires_in"]
            },
            msg=result["msg"]
        )

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    except Exception as exc:
        logger.exception("Error while sending payment OTP")

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )

@router.post("/verify")
def verify_payment_otp(
    request: VerifyOTPRequest,
    current_user=Depends(get_current_user),
):
    try:
        result = otp_service.verify_otp(
            str(current_user.id),
            request.tuition_fee_id,
            request.otp
        )

        return send_success_response(
            data={
                "verified": result["verified"]
            },
            msg=result["msg"]
        )

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    except Exception as exc:
        logger.exception("Error while verifying payment OTP")

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        )