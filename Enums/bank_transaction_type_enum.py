from enum import Enum

class BankTransactionTypeEnum(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"
