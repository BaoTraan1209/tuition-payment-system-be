from abc import ABC, abstractmethod
from Models.payment_log import PaymentLog

class IPaymentLogRepository(ABC):

    @abstractmethod
    def save(self, payment_log: PaymentLog) -> None:
        pass

    @abstractmethod
    def find_by_payment_id(self, payment_id: int) -> list[PaymentLog]:
        pass