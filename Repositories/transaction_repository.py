from sqlalchemy import text
from sqlalchemy.orm import Session


def get_transactions_by_payer(db: Session, payer_id: int):
    rows = db.execute(text("""
        SELECT transaction_id, payer_id, payment_id, type, amount, status, created_at, updated_at
        FROM transactions
        WHERE payer_id = :payer_id
        ORDER BY created_at DESC, transaction_id DESC
    """), {"payer_id": payer_id}).mappings().all()
    return [dict(row) for row in rows]
