from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from config.db import get_db
from Security.auth_dependency import get_current_user
from Security.admin_dependency import get_current_admin
from Services.tuition_fee_service import TuitionFeeService
from Helpers.response_helper import send_success_response

from schemas.tuition_fee_schema import (
    CreateTuitionFeeRequest,
    CreateTuitionFeeResponse,
    CreateTuitionFeesBulkRequest,
    TuitionFeeResponse
)

router = APIRouter(prefix="/api/tuition-fees", tags=["Tuition Fee"])

# Admin tạo khoản học phí
@router.post("/create")
def create_tuition_fee(
    data: CreateTuitionFeeRequest,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tuition_fee_service = TuitionFeeService(db)

    tuition_fee = tuition_fee_service.create_tuition_fee(
        user_id=data.user_id,
        title=data.title,
        amount=data.amount,
        due_date=data.due_date,
        description=data.description
    )

    response_data = CreateTuitionFeeResponse(
        id=tuition_fee.id,
        user_id=tuition_fee.user_id,
        title=tuition_fee.title,
        description=tuition_fee.description,
        amount=tuition_fee.amount,
        due_date=tuition_fee.due_date,
        status=tuition_fee.status
    )

    return send_success_response(
        data=response_data.model_dump(),
        msg="Tuition fee created successfully"
    )

# Admin tạo khoản học phí cho nhiều sinh viên cùng lúc
@router.post("/create-bulk")
def create_tuition_fees_bulk(
    data: CreateTuitionFeesBulkRequest,
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    tuition_fee_service = TuitionFeeService(db)

    tuition_fees = tuition_fee_service.create_tuition_fees_bulk(
        user_ids=data.user_ids,
        title=data.title,
        amount=data.amount,
        due_date=data.due_date,
        description=data.description
    )

    response_data = [
        TuitionFeeResponse(
            id=tf.id,
            user_id=tf.user_id,
            title=tf.title,
            description=tf.description,
            amount=tf.amount,
            due_date=tf.due_date,
            status=tf.status
        ).model_dump()
        for tf in tuition_fees
    ]

    return send_success_response(
        data=response_data,
        msg=f"Created {len(tuition_fees)} tuition fees successfully"
    )

# Sinh viên xem danh sách học phí
@router.get("")
def get_tuition_fees(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tuition_fees = TuitionFeeService(db).get_tuition_fees(
        user_id=str(current_user.id)
    )

    response_data = [
        TuitionFeeResponse.model_validate(item).model_dump()
        for item in tuition_fees
    ]

    return send_success_response(
        data=response_data,
        msg="Tuition fees retrieved successfully"
    )


# Sinh viên xem chi tiết học phí
@router.get("/{tuition_fee_id}")
def get_tuition_fee(
    tuition_fee_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tuition_fee = TuitionFeeService(db).get_tuition_fee(
        tuition_fee_id=tuition_fee_id,
        user_id=str(current_user.id)
    )

    response_data = TuitionFeeResponse.model_validate(tuition_fee)

    return send_success_response(
        data=response_data.model_dump(),
        msg="Tuition fee retrieved successfully"
    )