from dataclasses import dataclass
from uuid import uuid4


@dataclass(frozen=True)
class Order:
    order_id: str
    offer_id: str
    amount: str
    currency: str
    status: str = "pending"


def create_order(offer_id: str, amount: str, currency: str) -> Order:
    return Order(
        order_id=str(uuid4()),
        offer_id=offer_id,
        amount=amount,
        currency=currency,
    )
