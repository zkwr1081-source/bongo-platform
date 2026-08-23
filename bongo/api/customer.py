from bongo.api.services import public_service
from bongo.commerce.order import create_commerce_order


def prepare_service_order(service_id: str):
    service = public_service(service_id)

    if service is None:
        raise ValueError("Service not found")

    return create_commerce_order(
        service["service_id"],
        service["price"],
        service["currency"],
    )
