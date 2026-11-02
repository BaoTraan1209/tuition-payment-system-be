from enum import Enum

class PaymentEventEnum(str, Enum):
    CREATED = "CREATED"
    PAYMENT_SUCCESS = "PAYMENT_SUCCESS"
    PAYMENT_FAILED = "PAYMENT_FAILED"
