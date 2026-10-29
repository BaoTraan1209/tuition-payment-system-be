from sqlalchemy import text


def get_tuition_by_mssv(db, mssv: str):
    query = text("""
        SELECT
            t.tuition_id,
            s.student_id,
            s.mssv,
            s.fullname,
            t.amount,
            t.status,
            t.created_at,
            t.updated_at
        FROM students s
        JOIN tuitions t ON t.student_id = s.student_id
        WHERE s.mssv = :mssv
        ORDER BY t.created_at DESC, t.tuition_id DESC
    """)
    rows = db.execute(query, {"mssv": mssv}).mappings().all()
    return [dict(row) for row in rows]
