
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from config.db import get_db
from Security.auth_dependency import get_current_user
from schemas.user_schema import UserProfileResponse, UserProfileUpdate
from Services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_service = UserService(db)

    return user_service.get_profile(UUID(str(current_user.user_id)))


@router.patch("/me", response_model=UserProfileResponse)
def update_my_profile(
    data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_service = UserService(db)

    try:
        return user_service.edit_profile(
            UUID(str(current_user.user_id)),
            data.model_dump(exclude_unset=True),
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="The supplied profile data conflicts with an existing record."
        )
