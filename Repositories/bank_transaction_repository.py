from sqlalchemy.orm import Session

from Models.bank_transaction import BankTransaction
from Contracts.Repositories.bank_transaction_repository_interface import IBankTransactionRepository

class BankTransactionRepository(IBankTransactionRepository):
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, id: int) -> BankTransaction | None:
        return self.db.query(BankTransaction).filter(
            BankTransaction.id == id
        ).first()

    def find_by_payment_id(self, payment_id: int) -> BankTransaction | None:
        return self.db.query(BankTransaction).filter(
            BankTransaction.payment_id == payment_id
        ).first()

    def save(self, bank_transaction: BankTransaction) -> None:
        self.db.add(bank_transaction)
