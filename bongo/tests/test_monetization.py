from bongo.monetization.catalog import get_offer
from bongo.monetization.validation import validate_offer
from bongo.monetization.checkout import create_checkout


def test_starter_offer():
    offer = get_offer("bongo-starter")

    assert offer is not None
    assert offer["name"] == "BONGO Starter"
    assert offer["price"] == "5.00"
    assert offer["currency"] == "USD"


def test_offer_validation():
    offer = get_offer("bongo-starter")

    assert validate_offer(offer) is True


def test_checkout_creation():
    order = create_checkout("bongo-starter")

    assert order.offer_id == "bongo-starter"
    assert order.amount == "5.00"
    assert order.currency == "USD"
    assert order.status == "pending"
    assert order.order_id
