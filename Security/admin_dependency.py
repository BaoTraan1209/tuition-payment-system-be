
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import JWTError

from Security.jwt import decode_token

bearer = HTTPBearer(auto_error=False)


def get_current_admin(
    credentials=Depends(bearer)
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

        if payload.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="Không có quyền truy cập"
            )

        return payload

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Token không hợp lệ"
        )
