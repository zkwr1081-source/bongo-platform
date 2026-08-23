from dataclasses import dataclass
from uuid import uuid4

from .status import PaymentStatus


@dataclass
class CommerceOrder:
    order_id: str
    offer_id: str
    amount: str
    currency: str
    payment_status: PaymentStatus = PaymentStatus.PENDING


def create_commerce_order(offer_id: str, amount: str, currency: str):
    return CommerceOrder(
        order_id=str(uuid4()),
        offer_id=offer_id,
        amount=amount,
        currency=currency,
    )
