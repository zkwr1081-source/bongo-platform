from dataclasses import dataclass


@dataclass(frozen=True)
class Service:
    service_id: str
    name: str
    description: str
    price: str
    currency: str
    active: bool = True
