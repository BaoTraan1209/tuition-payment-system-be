from sqlalchemy.orm import Session

from Models.bank_account import BankAccount
from Contracts.Repositories.bank_account_repository_interface import IBankAccountRepository

class BankAccountRepository(IBankAccountRepository):
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, id: int) -> BankAccount | None:
        return self.db.query(BankAccount).filter(
            BankAccount.id == id
        ).first()

    def find_by_user_id(self, user_id: str) -> BankAccount | None:
        return self.db.query(BankAccount).filter(
            BankAccount.user_id == user_id
        ).first()

    def find_by_user_id_for_update(self, user_id: str) -> BankAccount | None:
        return self.db.query(BankAccount).filter(
            BankAccount.user_id == user_id
        ).with_for_update().first()

    def save(self, bank_account: BankAccount) -> None:
        self.db.add(bank_account)

    def update(self, bank_account: BankAccount) -> None:
        self.db.add(bank_account)
