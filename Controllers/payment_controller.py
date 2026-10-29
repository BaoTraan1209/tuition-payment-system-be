from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from config.db import get_db
from Security.auth_dependency import get_current_user
from Services.payment_service import create_payment_request, complete_payment

router = APIRouter(prefix="/payments", tags=["Payments"])


class PaymentRequest(BaseModel):
    tuition_id: int = Field(gt=0)


class PaymentConfirmation(BaseModel):
    payment_id: int = Field(gt=0)
    otp: str = Field(min_length=6, max_length=6, pattern=r"^[0-9]{6}$")


@router.post("")
def create_payment_endpoint(data: PaymentRequest, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        result = create_payment_request(db, int(current_user.payer_id), data.tuition_id)
        return {"success": True, "message": "Payment request created.", "data": result}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


@router.post("/confirm")
def confirm_payment_endpoint(data: PaymentConfirmation, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        result = complete_payment(db, int(current_user.payer_id), data.payment_id, data.otp)
        return {"success": True, "message": result["message"], "data": result}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))
