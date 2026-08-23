from .model import Service


SERVICES = {
    "bongo-starter": Service(
        service_id="bongo-starter",
        name="BONGO Starter",
        description="وصول تجريبي إلى خدمات وحلول BONGO المتكاملة.",
        price="5.00",
        currency="USD",
    ),
}


def list_services():
    return [
        service
        for service in SERVICES.values()
        if service.active
    ]


def get_service(service_id: str):
    return SERVICES.get(service_id)
