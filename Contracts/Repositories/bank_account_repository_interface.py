from abc import ABC, abstractmethod

from Models.bank_account import BankAccount

class IBankAccountRepository(ABC):
    @abstractmethod
    def find_by_id(self, id: int) -> BankAccount | None:
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> BankAccount | None:
        pass

    @abstractmethod
    def find_by_user_id_for_update(
        self,
        user_id: str
    ) -> BankAccount | None:
        pass

    @abstractmethod
    def save(self, bank_account: BankAccount) -> None:
        pass

    @abstractmethod
    def update(self, bank_account: BankAccount) -> None:
        pass