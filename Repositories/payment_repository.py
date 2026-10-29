from sqlalchemy import text
from sqlalchemy.orm import Session


def create_payment(db: Session, payer_id: int, tuition_id: int):
    """Create a pending payment only for an unpaid tuition belonging to payer."""
    tuition = db.execute(text("""
        SELECT t.tuition_id, t.student_id, t.amount, t.status
        FROM tuitions t
        JOIN payers py ON py.student_id = t.student_id
        WHERE t.tuition_id = :tuition_id AND py.payer_id = :payer_id
        FOR UPDATE
    """), {"tuition_id": tuition_id, "payer_id": payer_id}).mappings().first()
    if not tuition:
        raise ValueError("Tuition was not found for this payer.")
    if tuition["status"] != "UNPAID":
        raise ValueError("This tuition has already been paid.")
    existing = db.execute(text("""
        SELECT payment_id FROM payments
        WHERE tuition_id = :tuition_id AND status IN ('PENDING', 'PROCESSING', 'SUCCESS')
        ORDER BY payment_id DESC LIMIT 1
    """), {"tuition_id": tuition_id}).mappings().first()
    if existing:
        if existing["payment_id"]:
            raise ValueError("A payment already exists for this tuition. Use the existing payment or contact support.")
    result = db.execute(text("""
        INSERT INTO payments (payer_id, tuition_id, amount, status, created_at)
        VALUES (:payer_id, :tuition_id, :amount, 'PENDING', NOW())
    """), {"payer_id": payer_id, "tuition_id": tuition_id, "amount": tuition["amount"]})
    return {"payment_id": result.lastrowid, "tuition_id": tuition_id,
            "amount": float(tuition["amount"]), "status": "PENDING"}


def get_payment_for_payer(db: Session, payment_id: int, payer_id: int, lock: bool = False):
    suffix = " FOR UPDATE" if lock else ""
    row = db.execute(text(f"""
        SELECT payment_id, payer_id, tuition_id, amount, status, created_at, completed_at
        FROM payments WHERE payment_id = :payment_id AND payer_id = :payer_id{suffix}
    """), {"payment_id": payment_id, "payer_id": payer_id}).mappings().first()
    return dict(row) if row else None


def lock_account(db: Session, payer_id: int):
    row = db.execute(text("""
        SELECT account_id, payer_id, balance, status
        FROM accounts WHERE payer_id = :payer_id LIMIT 1 FOR UPDATE
    """), {"payer_id": payer_id}).mappings().first()
    return dict(row) if row else None


def debit_account(db: Session, payer_id: int, amount):
    result = db.execute(text("""
        UPDATE accounts SET balance = balance - :amount, updated_at = NOW()
        WHERE payer_id = :payer_id AND status = 'ACTIVE' AND balance >= :amount
    """), {"payer_id": payer_id, "amount": amount})
    return result.rowcount == 1


def mark_tuition_paid(db: Session, tuition_id: int):
    result = db.execute(text("""
        UPDATE tuitions SET status = 'PAID', updated_at = NOW()
        WHERE tuition_id = :tuition_id AND status = 'UNPAID'
    """), {"tuition_id": tuition_id})
    return result.rowcount == 1


def mark_payment_success(db: Session, payment_id: int):
    db.execute(text("""
        UPDATE payments SET status = 'SUCCESS', completed_at = NOW()
        WHERE payment_id = :payment_id AND status IN ('PENDING', 'PROCESSING')
    """), {"payment_id": payment_id})


def mark_payment_failed(db: Session, payment_id: int):
    db.execute(text("""
        UPDATE payments SET status = 'FAILED'
        WHERE payment_id = :payment_id AND status IN ('PENDING', 'PROCESSING')
    """), {"payment_id": payment_id})


def create_transaction(db: Session, payer_id: int, payment_id: int, amount):
    db.execute(text("""
        INSERT INTO transactions (payer_id, payment_id, type, amount, status, created_at, updated_at)
        VALUES (:payer_id, :payment_id, 'TUITION_PAYMENT', :amount, 'SUCCESS', NOW(), NOW())
    """), {"payer_id": payer_id, "payment_id": payment_id, "amount": amount})
