from bongo.api.services import public_services, public_service
from bongo.api.customer import prepare_service_order


def test_public_services():
    services = public_services()

    assert services
    assert services[0]["service_id"] == "bongo-starter"
    assert services[0]["active"] is True


def test_public_service():
    service = public_service("bongo-starter")

    assert service is not None
    assert service["price"] == "5.00"
    assert service["currency"] == "USD"


def test_customer_order():
    order = prepare_service_order("bongo-starter")

    assert order.offer_id == "bongo-starter"
    assert order.amount == "5.00"
    assert order.currency == "USD"
    assert order.payment_status.value == "pending"
