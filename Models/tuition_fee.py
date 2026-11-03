from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, DateTime, func

from config.db import Base
from Enums.tuition_fee_status_enum import TuitionFeeStatusEnum

class TuitionFee(Base):
    __tablename__ = "tuition_fees"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(
        String(36),
        ForeignKey("users.id"),
        nullable=False
    )

    title = Column(String(255), nullable=False)

    description = Column(Text, nullable=True)

    amount = Column(Integer, nullable=False)

    due_date = Column(Date, nullable=False)

    status = Column(
        String(20),
        default=TuitionFeeStatusEnum.UNPAID.value,
        nullable=False
    )

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