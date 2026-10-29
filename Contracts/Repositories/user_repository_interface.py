
from abc import ABC, abstractmethod
from uuid import UUID

from Models.user import User

class IUserRepository(ABC):
    @abstractmethod
    def find_by_id(self, id: str) -> User | None:
        pass

    @abstractmethod
    def find_by_username(self, username: str) -> User | None:
        pass

    @abstractmethod
    def save(self, user: User) -> None:
        pass