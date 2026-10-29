from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.db import get_db
from Security.auth_dependency import get_current_user
from schemas.account_schema import AccountResponse, AccountBalanceResponse
from Services.account_service import get_payer_account, get_payer_balance

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get("/me", response_model=AccountResponse)
def get_my_account(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return get_payer_account(db, int(current_user.payer_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/me/balance", response_model=AccountBalanceResponse)
def get_my_balance(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return get_payer_balance(db, int(current_user.payer_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
