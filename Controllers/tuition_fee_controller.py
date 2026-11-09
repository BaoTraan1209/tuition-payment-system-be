from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.db import get_db
from Security.auth_dependency import get_current_user
from Security.admin_dependency import get_current_admin
from Services.tuition_fee_service import TuitionFeeService
from Helpers.response_helper import send_success_response

from Repositories.user_repository import UserRepository
from Models.tuition_fee import TuitionFee
from Models.user import User

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

@router.get("/student/{mssv}")
def get_tuition_fees_by_mssv(
    mssv: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Chuẩn hóa MSSV để tránh lỗi do khoảng trắng hoặc chữ thường
    normalized_mssv = mssv.strip().upper()

    # Tìm sinh viên theo MSSV
    student = UserRepository(db).find_by_mssv(normalized_mssv)

    if not student:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy sinh viên với MSSV này",
        )

    # UUID vẫn là khóa liên kết nội bộ giữa user và tuition fee
    fees = (
        db.query(TuitionFee)
        .filter(TuitionFee.user_id == str(student.id))
        .order_by(TuitionFee.due_date.asc())
        .all()
    )

    return send_success_response(
        data={
            "student": {
                "fullname": student.fullname,
                "mssv": student.mssv,
            },
            "fees": [
                TuitionFeeResponse.model_validate(fee).model_dump()
                for fee in fees
            ],
        },
        msg="Tuition fees retrieved successfully",
    )
    
@router.get("/admin/all")
def get_all_tuition_fees_for_admin(
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(TuitionFee, User)
        .join(User, TuitionFee.user_id == User.id)
        .order_by(TuitionFee.created_at.desc())
        .all()
    )

    data = [
        {
            "id": fee.id,
            "title": fee.title,
            "description": fee.description,
            "amount": fee.amount,
            "due_date": fee.due_date.isoformat() if fee.due_date else None,
            "status": fee.status,
            "mssv": student.mssv,
            "fullname": student.fullname,
            "created_at": fee.created_at.isoformat() if fee.created_at else None,
        }
        for fee, student in rows
    ]

    return send_success_response(
        data=data,
        msg="Tuition fees retrieved successfully",
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