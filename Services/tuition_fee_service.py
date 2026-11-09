from datetime import date
from typing import List
from sqlalchemy.orm import Session

from Models.tuition_fee import TuitionFee
from Repositories.tuition_fee_repository import TuitionFeeRepository
from Enums.tuition_fee_status_enum import TuitionFeeStatusEnum


class TuitionFeeService:

    def __init__(self, db: Session):
        self.db = db
        self.tuition_fee_repository = TuitionFeeRepository(db)

    def create_tuition_fee(
        self,
        user_id: str,
        title: str,
        amount: int,
        due_date: date,
        description: str | None = None
    ) -> TuitionFee:

        try:
            tuition_fee = TuitionFee(
                user_id=user_id,
                title=title,
                description=description,
                amount=amount,
                due_date=due_date,
                status=TuitionFeeStatusEnum.UNPAID.value
            )

            self.tuition_fee_repository.save(tuition_fee)

            self.db.commit()
            self.db.refresh(tuition_fee)

            return tuition_fee

        except Exception:
            self.db.rollback()
            raise

    def create_tuition_fees_bulk(
        self,
        user_ids: List[str],
        title: str,
        amount: int,
        due_date: date,
        description: str | None = None
    ) -> List[TuitionFee]:

        try:
            tuition_fees = [
                TuitionFee(
                    user_id=user_id,
                    title=title,
                    description=description,
                    amount=amount,
                    due_date=due_date,
                    status=TuitionFeeStatusEnum.UNPAID.value
                )
                for user_id in user_ids
            ]

            self.tuition_fee_repository.save_all(tuition_fees)

            self.db.commit()
            
            return tuition_fees

        except Exception:
            self.db.rollback()
            raise

    def get_tuition_fees(self, user_id: str) -> list[TuitionFee]:
        return self.tuition_fee_repository.find_by_user_id(user_id)

    def get_tuition_fee(
        self,
        tuition_fee_id: int,
        user_id: str
    ) -> TuitionFee:

        tuition_fee = self.tuition_fee_repository.find_by_id(tuition_fee_id)

        if not tuition_fee or str(tuition_fee.user_id) != str(user_id):
            raise ValueError("Tuition fee not found")

        return tuition_fee