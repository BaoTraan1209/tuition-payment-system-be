from sqlalchemy.orm import Session

from Models.payment_log import PaymentLog
from Contracts.Repositories.payment_log_repository_interface import IPaymentLogRepository

class PaymentLogRepository(IPaymentLogRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, payment_log: PaymentLog) -> None:
        self.db.add(payment_log)
        self.db.commit()
        self.db.refresh(payment_log)

    def find_by_payment_id(self, payment_id: int) -> list[PaymentLog]:
        return self.db.query(PaymentLog).filter(
            PaymentLog.payment_id == payment_id
        ).order_by(
            PaymentLog.created_at.desc()
        ).all()