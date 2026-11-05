from abc import ABC, abstractmethod

from Models.tuition_fee import TuitionFee

class ITuitionFeeRepository(ABC):
    @abstractmethod
    def find_by_id(self, id: int) -> TuitionFee | None:
        pass

    @abstractmethod
    def find_by_id_for_update(self, id: int) -> TuitionFee | None:
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> list[TuitionFee]:
        pass

    @abstractmethod
    def save(self, tuition_fee: TuitionFee) -> None:
        pass

    @abstractmethod
    def update(self, tuition_fee: TuitionFee) -> None:
        pass