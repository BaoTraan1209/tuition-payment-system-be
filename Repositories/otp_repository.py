from sqlalchemy import text
from sqlalchemy.orm import Session


def get_payment_email(db: Session, payment_id: int, payer_id: int | None = None):
    query = text("""
        SELECT p.payment_id, p.payer_id, p.status, py.email
        FROM payments p
        JOIN payers py ON py.payer_id = p.payer_id
        WHERE p.payment_id = :payment_id
          AND (:payer_id IS NULL OR p.payer_id = :payer_id)
    """)

    result = db.execute(
        query,
        {"payment_id": payment_id, "payer_id": payer_id}
    ).mappings().first()

    return dict(result) if result else None


def invalidate_previous_otps(db: Session, payment_id: int):
    query = text("""
        UPDATE otps
        SET used = TRUE
        WHERE payment_id = :payment_id
          AND used = FALSE
    """)

    db.execute(query, {"payment_id": payment_id})


def create_otp_record(
    db: Session,
    payment_id: int,
    otp_hash: str,
    expires_at
):
    query = text("""
        INSERT INTO otps (
            payment_id,
            otp_hash,
            expires_at,
            used,
            attempt_count
        )
        VALUES (
            :payment_id,
            :otp_hash,
            :expires_at,
            FALSE,
            0
        )
    """)

    result = db.execute(
        query,
        {
            "payment_id": payment_id,
            "otp_hash": otp_hash,
            "expires_at": expires_at
        }
    )

    return result.lastrowid


def get_latest_otp_for_update(db: Session, payment_id: int):
    query = text("""
        SELECT
            otp_id,
            payment_id,
            otp_hash,
            expires_at,
            used,
            attempt_count
        FROM otps
        WHERE payment_id = :payment_id
        ORDER BY otp_id DESC
        LIMIT 1
        FOR UPDATE
    """)

    result = db.execute(
        query,
        {"payment_id": payment_id}
    ).mappings().first()

    return dict(result) if result else None


def increase_otp_attempts(db: Session, otp_id: int):
    query = text("""
        UPDATE otps
        SET attempt_count = attempt_count + 1
        WHERE otp_id = :otp_id
    """)

    db.execute(query, {"otp_id": otp_id})


def mark_otp_used(db: Session, otp_id: int):
    query = text("""
        UPDATE otps
        SET used = TRUE
        WHERE otp_id = :otp_id
    """)

    db.execute(query, {"otp_id": otp_id})


def get_otp_by_id(db: Session, otp_id: int):
    query = text("""
        SELECT otp_id, used
        FROM otps
        WHERE otp_id = :otp_id
    """)

    result = db.execute(
        query,
        {"otp_id": otp_id}
    ).mappings().first()

    return dict(result) if result else None
