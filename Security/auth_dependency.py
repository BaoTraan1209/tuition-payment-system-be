from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import JWTError
from sqlalchemy.orm import Session

from config.db import get_db
from Repositories.user_repository import UserRepository
from Security.jwt import decode_token

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials=Depends(bearer),
    db: Session = Depends(get_db)
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Chưa đăng nhập"
        )

    try:
        payload = decode_token(credentials.credentials)

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=401,
                detail="Token không hợp lệ"
            )

        user_id = str(UUID(payload["sub"]))
        
    except (JWTError, KeyError, ValueError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Token không hợp lệ"
        )

    user_repository = UserRepository(db)
    user = user_repository.find_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Tài khoản không tồn tại"
        )

    return user