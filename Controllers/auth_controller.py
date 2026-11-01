from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from jose import JWTError
from pydantic import BaseModel

from config.db import get_db
from schemas.auth_schema import LoginRequest
from Services.auth_service import AuthService
from Services.user_service import UserService
from Security.auth_dependency import get_current_user
from Security.jwt import (
    decode_token,
    create_access_token,
    create_refresh_token,
    get_token_ttl,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from Helpers.response_helper import send_success_response

from schemas.user_schema import UserProfileResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class RefreshTokenRequest(BaseModel):
    refresh_token: str

@router.post("/login")
def login(
    data: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)

    user = auth_service.login(
        data.username,
        data.password,
        request
    )

    user_data = UserProfileResponse.model_validate(user).model_dump()

    result = {
        "access_token": create_access_token(str(user.id)),
        "refresh_token": create_refresh_token(str(user.id)),
        "token_type": "bearer",
        "expires_in": get_token_ttl(),
        "refresh_expires_in": REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        "user": user_data
    }

    return send_success_response(
        data=result,
        msg="Login successful"
    )

@router.post("/refresh")
def refresh(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Nhận refresh_token (body JSON), trả về access_token mới."""
    try:
        payload = decode_token(data.refresh_token)
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Refresh token expired or invalid"
        )

    if payload.get("type") != "refresh" or not payload.get("sub"):
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    user_id = payload["sub"]

    # Tài khoản bị xoá thì không cấp lại token
    if UserService(db).user_repository.find_by_id(user_id) is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    result = {
        "access_token": create_access_token(user_id),
        "token_type": "bearer",
        "expires_in": get_token_ttl()
    }

    return send_success_response(
        data=result,
        msg="Refresh successful"
    )

@router.get("/me")
def get_profile(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    user = user_service.get_profile(current_user.id)

    return send_success_response(
        data=UserProfileResponse.model_validate(user).model_dump(),
        msg="Get profile successful"
    )