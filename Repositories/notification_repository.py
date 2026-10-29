from sqlalchemy import text


def get_notifications(db, payer_id: int):
    rows = db.execute(text("""
        SELECT notification_id, payer_id, title, message, type, is_read, created_at
        FROM notifications
        WHERE payer_id = :payer_id
        ORDER BY created_at DESC, notification_id DESC
    """), {"payer_id": payer_id}).mappings().all()
    return [dict(row) for row in rows]


def mark_read(db, payer_id: int, notification_id: int):
    result = db.execute(text("""
        UPDATE notifications
        SET is_read = 1
        WHERE notification_id = :notification_id AND payer_id = :payer_id
    """), {"notification_id": notification_id, "payer_id": payer_id})
    db.commit()
    return result.rowcount == 1


def create_notification(db, payer_id: int, title: str, message: str, kind: str = "INFO"):
    result = db.execute(text("""
        INSERT INTO notifications (payer_id, title, message, type, is_read, created_at)
        VALUES (:payer_id, :title, :message, :type, 0, NOW())
    """), {"payer_id": payer_id, "title": title, "message": message, "type": kind})
    db.commit()
    return result.lastrowid


def get_owned_tuition_for_reminder(db, payer_id: int, tuition_id: int):
    row = db.execute(text("""
        SELECT t.tuition_id, t.amount, t.status, s.mssv, s.fullname, p.email
        FROM tuitions t
        JOIN students s ON s.student_id = t.student_id
        JOIN payers p ON p.student_id = s.student_id
        WHERE t.tuition_id = :tuition_id AND p.payer_id = :payer_id
        LIMIT 1
    """), {"tuition_id": tuition_id, "payer_id": payer_id}).mappings().first()
    return dict(row) if row else None
