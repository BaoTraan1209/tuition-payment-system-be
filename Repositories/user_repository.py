
from uuid import UUID

from sqlalchemy.orm import Session

from Models.user import User
from Contracts.Repositories.user_repository_interface import IUserRepository


class UserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, id: str) -> User | None:
        return (
            self.db.query(User)
            .filter(User.id == id)
            .first()
        )

    def find_by_username(self, username: str) -> User | None:
        return (
            self.db.query(User)
            .filter(User.username == username)
            .first()
        )

    def save(self, user: User) -> None:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
