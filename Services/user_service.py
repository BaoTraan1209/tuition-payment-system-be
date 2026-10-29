from uuid import UUID

from fastapi import HTTPException
from starlette import status
from sqlalchemy.orm import Session

from Repositories.user_repository import UserRepository


class UserService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)

    def get_profile(self, id: UUID):
        if not id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID."
            )

        user = self.user_repository.find_by_id(id)
        print("Found user:", user)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        return user

    def edit_profile(self, id: UUID, updates: dict):
        user = self.user_repository.find_by_id(id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        allowed = {"fullname", "phone", "email"}
        values = {
            key: value
            for key, value in updates.items()
            if key in allowed
        }

        if not values:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide at least one profile field to update."
            )

        if "fullname" in values and values["fullname"] is not None:
            values["fullname"] = values["fullname"].strip()

            if not values["fullname"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Full name cannot be empty."
                )

        if "phone" in values and values["phone"] is not None:
            values["phone"] = values["phone"].strip() or None

        if "email" in values and values["email"] is not None:
            values["email"] = values["email"].strip().lower()

            if values["email"] and (
                "@" not in values["email"]
                or "." not in values["email"].rsplit("@", 1)[-1]
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email address is invalid."
                )

        for key, value in values.items():
            setattr(user, key, value)

        self.user_repository.save(user)

        return user
