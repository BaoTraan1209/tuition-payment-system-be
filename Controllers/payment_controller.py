from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from config.db import get_db
from Security.auth_dependency import get_current_user
from Services.payment_service import PaymentService
from Helpers.response_helper import send_success_response

from schemas.payment_schema import (
    CreatePaymentRequest,
    CreatePaymentResponse
)

router = APIRouter(prefix="/api/payment", tags=["Payment"])

@router.post("/create")
def create_payment(
    data: CreatePaymentRequest,
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    payment_service = PaymentService(db)

    ip_address = request.client.host if request.client else "127.0.0.1"

    result = payment_service.create_payment(
        user_id=str(current_user.id),
        tuition_fee_id=data.tuition_fee_id,
        ip_address=ip_address
    )

    response_data = CreatePaymentResponse(
        order_id=result["payment"].order_id,
        amount=result["payment"].amount,
        status=result["payment"].status,
        payment_url=result["payment_url"]
    )

    return send_success_response(
        data=response_data.model_dump(),
        msg="Payment URL created successfully"
    )

@router.get("/history")
def get_payment_history(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = PaymentService(db).get_payment_history(
        user_id=str(current_user.id)
    )

    return send_success_response(
        data=result,
        msg="Payment history retrieved successfully"
    )

@router.get("/vnpay/return")
def vnpay_return(
    request: Request,
    db: Session = Depends(get_db)
):
    params = dict(request.query_params)

    return PaymentService(db).handle_return(params)


@router.get("/vnpay/ipn")
def vnpay_ipn(
    request: Request,
    db: Session = Depends(get_db)
):
    params = dict(request.query_params)

    return PaymentService(db).handle_ipn(params)


@router.get("/status/{order_id}")
def get_payment_status(
    order_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = PaymentService(db).get_payment_status(
        order_id=order_id,
        user_id=str(current_user.id)
    )

    return send_success_response(
        data=result,
        msg="Payment status retrieved successfully"
    )