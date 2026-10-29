from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.db import get_db
from Security.auth_dependency import get_current_user
from Services.tuition_service import get_student_tuitions, get_student_tuition_status

router = APIRouter(prefix="/tuitions", tags=["Tuitions"])


def _assert_owns_mssv(db: Session, payer_id: int, mssv: str) -> None:
    from sqlalchemy import text
    row = db.execute(text("""
        SELECT 1
        FROM payers p
        JOIN students s ON s.student_id = p.student_id
        WHERE p.payer_id = :payer_id AND s.mssv = :mssv
        LIMIT 1
    """), {"payer_id": payer_id, "mssv": mssv.strip()}).first()
    if not row:
        raise HTTPException(status_code=403, detail="Bạn không có quyền xem học phí của MSSV này.")


@router.get("/{mssv}")
def get_tuitions(
    mssv: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _assert_owns_mssv(db, int(current_user.payer_id), mssv)
    try:
        data = get_student_tuitions(db, mssv)
        return {"success": True, "message": "Tuition records retrieved successfully.", "data": data}
    except ValueError as error:
        # Empty tuition list is valid: UI can display an empty table.
        if str(error) == "No tuition records found.":
            return {"success": True, "message": "No tuition records found.", "data": []}
        raise HTTPException(status_code=404, detail=str(error))


@router.get("/{mssv}/status")
def get_tuition_status(
    mssv: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    _assert_owns_mssv(db, int(current_user.payer_id), mssv)
    try:
        data = get_student_tuition_status(db, mssv)
        return {"success": True, "data": data}
    except ValueError as error:
        if str(error) == "No tuition records found.":
            return {"success": True, "data": []}
        raise HTTPException(status_code=404, detail=str(error))
