
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func

from config.db import Base
from Enums.bank_transaction_type_enum import BankTransactionTypeEnum

class BankTransaction(Base):
    __tablename__ = "bank_transactions"

    id = Column(Integer, primary_key=True, autoincrement=True)

    bank_account_id = Column(
        Integer,
        ForeignKey("bank_accounts.id"),
        nullable=False
    )

    payment_id = Column(
        Integer,
        ForeignKey("payments.id"),
        unique=True,
        nullable=False
    )

    amount = Column(Integer, nullable=False)

    balance_before = Column(Integer, nullable=False)

    balance_after = Column(Integer, nullable=False)

    transaction_type = Column(
        String(20),
        default=BankTransactionTypeEnum.DEBIT.value,
        nullable=False
    )

    description = Column(String(255), nullable=True)

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
