from sqlalchemy.orm import Session

from Repositories.account_repository import get_account_by_payer_id


def get_payer_account(db: Session, payer_id: int):
    if payer_id <= 0:
        raise ValueError("Invalid payer ID.")

    account = get_account_by_payer_id(db, payer_id)
    if account is None:
        raise ValueError("Payment account was not found.")

    return {
        "account_id": account.account_id,
        "payer_id": account.payer_id,
        "balance": float(account.balance or 0),
        "status": account.status,
    }


def get_payer_balance(db: Session, payer_id: int):
    account = get_payer_account(db, payer_id)
    return {
        "payer_id": account["payer_id"],
        "balance": account["balance"],
        "status": account["status"],
    }
