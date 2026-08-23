from dataclasses import dataclass
from .status import PaymentStatus


@dataclass(frozen=True)
class Payment:
    payment_id: str
    order_id: str
    amount: str
    currency: str
    status: PaymentStatus
    provider: str = "pending"
