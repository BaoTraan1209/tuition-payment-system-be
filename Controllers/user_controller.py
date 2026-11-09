
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from config.db import get_db
from Security.auth_dependency import get_current_user
from schemas.user_schema import StudentResponse, UserProfileResponse, UserProfileUpdate
from Services.user_service import UserService
from Security.admin_dependency import get_current_admin

router = APIRouter(prefix="/api/user", tags=["Users"])

@router.get("/me", response_model=UserProfileResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_service = UserService(db)

    return user_service.get_profile(current_user.id)


@router.patch("/me", response_model=UserProfileResponse)
def update_my_profile(
    data: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_service = UserService(db)

    try:
        return user_service.edit_profile(
            current_user.id,
            data.model_dump(exclude_unset=True),
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="The supplied profile data conflicts with an existing record."
        )

@router.get("/students", response_model=list[StudentResponse])
def get_all_students(
    current_admin=Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return UserService(db).get_all_students()