from sqlalchemy.orm import Session

from Models.tuition_fee import TuitionFee

from Contracts.Repositories.tuition_fee_repository_interface import ITuitionFeeRepository

class TuitionFeeRepository(ITuitionFeeRepository):
    def __init__(self, db: Session):
        self.db = db

    def find_by_id(self, id: int) -> TuitionFee | None:
        return self.db.query(TuitionFee).filter(
            TuitionFee.id == id
        ).first()

    def find_by_id_for_update(self, id: int) -> TuitionFee | None:
        return (
            self.db.query(TuitionFee)
            .filter(TuitionFee.id == id)
            .with_for_update()
            .first()
        )

    def find_by_user_id(self, user_id: str) -> list[TuitionFee]:
        return (
            self.db.query(TuitionFee)
            .filter(TuitionFee.user_id == user_id)
            .order_by(TuitionFee.created_at.desc())
            .all()
        )

    def save(self, tuition_fee: TuitionFee) -> None:
        self.db.add(tuition_fee)
        self.db.flush()
        self.db.refresh(tuition_fee)

    def update(self, tuition_fee: TuitionFee) -> None:
        self.db.flush()
        self.db.refresh(tuition_fee)

    def save_all(self, tuition_fees: list[TuitionFee]) -> None:
        self.db.add_all(tuition_fees)
        self.db.flush()
        for tuition_fee in tuition_fees:
            self.db.refresh(tuition_fee)