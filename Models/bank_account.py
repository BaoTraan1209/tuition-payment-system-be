from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from config.db import Base


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        String(36),
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    balance = Column(Integer, default=0, nullable=False)

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )