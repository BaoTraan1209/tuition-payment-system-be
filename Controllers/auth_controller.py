from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
from pydantic import BaseModel

from config.db import get_db
from schemas.auth_schema import LoginRequest
from Services.auth_service import AuthService
from Services.user_service import UserService
from Security.auth_dependency import get_current_user
from Security.jwt import decode_token, create_access_token, get_token_ttl
from Helpers.response_helper import send_success_response

from schemas.user_schema import UserProfileResponse

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
bearer = HTTPBearer()

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
        "token_type": "bearer",
        "expires_in": get_token_ttl(),
        "user": user_data
    }

    return send_success_response(
        data=result,
        msg="Login successful"
    )

@router.post("/refresh")
def refresh(
    credentials: HTTPAuthorizationCredentials = Depends(bearer)
):
    try:
        payload = decode_token(credentials.credentials)

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=401,
                detail="Invalid access token"
            )

        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid access token"
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

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Access token expired or invalid"
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