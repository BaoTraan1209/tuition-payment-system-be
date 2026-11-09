from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.db import get_db
from Security.auth_dependency import get_current_user
from Models.bank_account import BankAccount

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get("/me")
def get_my_account(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    bank_account = (
        db.query(BankAccount)
        .filter(BankAccount.user_id == str(current_user.id))
        .first()
    )

    if bank_account is None:
        raise HTTPException(
            status_code=404,
            detail="Bank account not found"
        )

    return {
        "id": bank_account.id,
        "user_id": str(bank_account.user_id),
        "balance": bank_account.balance
    }


@router.get("/me/balance")
def get_my_balance(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    bank_account = (
        db.query(BankAccount)
        .filter(BankAccount.user_id == str(current_user.id))
        .first()
    )

    if bank_account is None:
        raise HTTPException(
            status_code=404,
            detail="Bank account not found"
        )

    return {
        "balance": bank_account.balance
    }