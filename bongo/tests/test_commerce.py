from bongo.commerce.order import create_commerce_order
from bongo.commerce.status import PaymentStatus
from bongo.commerce.verification import (
    verify_payment,
    can_deliver_service,
)


def test_create_order():
    order = create_commerce_order(
        "bongo-starter",
        "5.00",
        "USD",
    )

    assert order.offer_id == "bongo-starter"
    assert order.amount == "5.00"
    assert order.currency == "USD"
    assert order.payment_status == PaymentStatus.PENDING
    assert order.order_id


def test_pending_payment_is_not_delivered():
    assert verify_payment(PaymentStatus.PENDING) is False
    assert can_deliver_service(PaymentStatus.PENDING) is False


def test_paid_payment_can_be_delivered():
    assert verify_payment(PaymentStatus.PAID) is True
    assert can_deliver_service(PaymentStatus.PAID) is True
