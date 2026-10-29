from sqlalchemy.orm import Session
from Repositories.transaction_repository import get_transactions_by_payer


def get_payer_transactions(db: Session, payer_id: int):
    if payer_id <= 0:
        raise ValueError("Payer ID must be greater than zero.")
    return get_transactions_by_payer(db, payer_id)
