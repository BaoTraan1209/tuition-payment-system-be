from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func

from config.db import Base
from Enums.payment_status_enum import PaymentStatusEnum


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, autoincrement=True)

    order_id = Column(String(100), unique=True, nullable=False)

    user_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False
    )

    tuition_fee_id = Column(
        Integer,
        ForeignKey("tuition_fees.id"),
        nullable=False
    )

    amount = Column(Integer, nullable=False)

    status = Column(
        String(20),
        default=PaymentStatusEnum.PENDING.value,
        nullable=False
    )

    vnp_transaction_no = Column(String(100), nullable=True)

    response_code = Column(String(10), nullable=True)

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