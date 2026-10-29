from sqlalchemy.orm import Session

from Models.account import Account


def get_account_by_payer_id(db: Session, payer_id: int):
    return db.query(Account).filter(Account.payer_id == payer_id).first()
