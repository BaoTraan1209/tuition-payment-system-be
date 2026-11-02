from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, func
from config.db import Base


class PaymentLog(Base):
    __tablename__ = "payment_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    payment_id = Column(
        Integer,
        ForeignKey("payments.id"),
        nullable=False
    )

    event = Column(String(50), nullable=False)

    response_code = Column(String(10), nullable=True)

    transaction_no = Column(String(100), nullable=True)

    message = Column(Text, nullable=True)

    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )