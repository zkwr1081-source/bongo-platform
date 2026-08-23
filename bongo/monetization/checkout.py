from .catalog import get_offer
from .validation import validate_offer
from .order import create_order


def create_checkout(offer_id: str):
    offer = get_offer(offer_id)

    validate_offer(offer)

    return create_order(
        offer_id=offer_id,
        amount=offer["price"],
        currency=offer["currency"],
    )
