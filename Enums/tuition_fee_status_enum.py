from enum import Enum

class TuitionFeeStatusEnum(str, Enum):
    UNPAID = "UNPAID"
    PAID = "PAID"
    OVERDUE = "OVERDUE"