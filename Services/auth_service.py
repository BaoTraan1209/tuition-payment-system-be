from fastapi import HTTPException, Request
from starlette import status
from sqlalchemy.orm import Session

from Repositories.user_repository import UserRepository
from Security.password import verify_password

class AuthService:
    def __init__(self, db: Session):
        self.user_repository = UserRepository(db)

    def login(
        self,
        username: str,
        password: str,
        request: Request
    ):
        user = self.user_repository.find_by_username(username)

        if user is None or not verify_password(
            password,
            user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized"
            )

        return user