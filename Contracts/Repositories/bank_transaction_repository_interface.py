from abc import ABC, abstractmethod

from Models.bank_transaction import BankTransaction

class IBankTransactionRepository(ABC):
    @abstractmethod
    def find_by_id(self, id: int) -> BankTransaction | None:
        pass

    @abstractmethod
    def find_by_payment_id(
        self,
        payment_id: int
    ) -> BankTransaction | None:
        pass

    @abstractmethod
    def save(self, bank_transaction: BankTransaction) -> None:
        pass