#ánh xạ bảg AccountDB
from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey
from config.db import Base

class Account(Base):
    __tablename__ = "accounts"

    account_id = Column(Integer, primary_key=True)
    payer_id = Column(Integer, ForeignKey("payers.payer_id"), unique=True)
    balance = Column(Numeric(15, 2))
    status = Column(String(20))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)