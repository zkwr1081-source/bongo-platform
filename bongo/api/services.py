from dataclasses import asdict

from bongo.services.catalog import list_services, get_service


def public_services():
    return [
        asdict(service)
        for service in list_services()
    ]


def public_service(service_id: str):
    service = get_service(service_id)

    if service is None or not service.active:
        return None

    return asdict(service)
