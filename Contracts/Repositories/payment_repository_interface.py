from abc import ABC, abstractmethod

from Models.payment import Payment

class IPaymentRepository(ABC):
    @abstractmethod
    def find_by_id(self, id: int) -> Payment | None:
        pass

    @abstractmethod
    def find_by_order_id(self, order_id: str) -> Payment | None:
        pass

    @abstractmethod
    def find_by_order_id_for_update(self, order_id: str) -> Payment | None:
        pass

    @abstractmethod
    def find_by_user_id(self, user_id: str) -> list[Payment]:
        pass

    @abstractmethod
    def find_pending_by_tuition_fee_id(
        self,
        tuition_fee_id: int
    ) -> Payment | None:
        pass

    @abstractmethod
    def save(self, payment: Payment) -> None:
        pass

    @abstractmethod
    def update(self, payment: Payment) -> None:
        pass