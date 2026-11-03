from sqlalchemy.orm import Session

from Models.payment import Payment
from Contracts.Repositories.payment_repository_interface import IPaymentRepository


class PaymentRepository(IPaymentRepository):

    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, id: int) -> Payment | None:
        return self.db.query(Payment).filter(
            Payment.id == id
        ).first()

    def find_by_order_id(self, order_id: str) -> Payment | None:
        return self.db.query(Payment).filter(
            Payment.order_id == order_id
        ).first()

    def find_by_user_id(self, user_id: str) -> list[Payment]:
        return (
            self.db.query(Payment)
            .filter(Payment.user_id == user_id)
            .order_by(Payment.created_at.desc())
            .all()
        )

    def save(self, payment: Payment) -> None:
        self.db.add(payment)
        self.db.flush()
        self.db.refresh(payment)

    def update(self, payment: Payment) -> None:
        self.db.flush()
        self.db.refresh(payment)