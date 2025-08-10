from enum import Enum, auto


class PaymentType(Enum):
    CREDIT_CARD = auto()
    CASH = auto()
    CHECK = auto()
    OTHER = auto()


class CustomerType(Enum):
    REGULAR = auto()
    VIP = auto()
