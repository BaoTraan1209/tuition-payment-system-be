from Repositories.tuition_repository import get_tuition_by_mssv


VALID_TUITION_STATUSES = {"UNPAID", "PAID", "PENDING", "OVERDUE", "CANCELLED"}


def get_student_tuitions(db, mssv: str):
    normalized = (mssv or "").strip()
    if not normalized:
        raise ValueError("MSSV is required.")

    rows = get_tuition_by_mssv(db, normalized)
    # No records is not a server failure; frontend should render an empty table.
    return rows


def get_student_tuition_status(db, mssv: str):
    rows = get_student_tuitions(db, mssv)
    result = []
    for row in rows:
        status = str(row.get("status") or "UNPAID").upper()
        result.append({
            "tuition_id": row.get("tuition_id"),
            "student_id": row.get("student_id"),
            "mssv": row.get("mssv"),
            "amount": float(row.get("amount") or 0),
            "status": status,
            "is_paid": status == "PAID",
            "is_payable": status == "UNPAID",
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        })
    return result
