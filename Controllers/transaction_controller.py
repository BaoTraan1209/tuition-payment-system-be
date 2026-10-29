from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from config.db import get_db
from Security.auth_dependency import get_current_user
from Services.transaction_service import get_payer_transactions

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("/me")
def get_my_transactions(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        transactions = get_payer_transactions(db, int(current_user.payer_id))
        return {"success": True, "message": "Transactions retrieved successfully.", "data": transactions}
    except Exception:
        raise HTTPException(status_code=500, detail="Unable to retrieve transactions.")
