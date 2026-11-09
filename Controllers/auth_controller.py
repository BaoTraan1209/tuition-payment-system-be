import secrets

from config.setting import USERNAME_ADMIN, PASSWORD_ADMIN
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from jose import JWTError


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




@router.post("/login")
def login(
    data: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    # Ưu tiên kiểm tra Admin trong .env
    username_valid = secrets.compare_digest(
        data.username,
        USERNAME_ADMIN
    )


    password_valid = secrets.compare_digest(
        data.password,
        PASSWORD_ADMIN
    )


    if username_valid and password_valid:
        response.set_cookie(
            key="refresh_token",
            value=create_refresh_token("admin", "admin"),
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            path="/api/auth"
        )


        result = {
            "access_token": create_access_token("admin", "admin"),
            "token_type": "bearer",
            "expires_in": get_token_ttl(),
            "role": "admin",
            "user": {
                "id": "admin",
                "username": USERNAME_ADMIN
            }
        }


        return send_success_response(
            data=result,
            msg="Admin login successful"
        )


    auth_service = AuthService(db)


    user = auth_service.login(
        data.username,
        data.password,
        request
    )


    user_data = UserProfileResponse.model_validate(user).model_dump()


    response.set_cookie(
        key="refresh_token",
        value=create_refresh_token(str(user.id), "student"),
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/api/auth"
    )


    result = {
        "access_token": create_access_token(str(user.id), "student"),
        "token_type": "bearer",
        "expires_in": get_token_ttl(),
        "role": "student",
        "user": user_data
    }


    return send_success_response(
        data=result,
        msg="Login successful"
    )




@router.post("/refresh")
def refresh(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    refresh_token = request.cookies.get("refresh_token")


    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token missing"
        )


    try:
        payload = decode_token(refresh_token)
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
    role = payload.get("role")


    if role == "admin":
        response.set_cookie(
            key="refresh_token",
            value=create_refresh_token("admin", "admin"),
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            path="/api/auth"
        )


        result = {
            "access_token": create_access_token("admin", "admin"),
            "token_type": "bearer",
            "expires_in": get_token_ttl()
        }


        return send_success_response(
            data=result,
            msg="Refresh successful"
        )


    if role != "student":
        raise HTTPException(
            status_code=401,
            detail="Invalid token role"
        )


    if UserService(db).user_repository.find_by_id(user_id) is None:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )


    result = {
        "access_token": create_access_token(user_id, "student"),
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




