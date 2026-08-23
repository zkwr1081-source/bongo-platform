from dataclasses import dataclass


@dataclass(frozen=True)
class Offer:
    name: str
    description: str
    price: str
    currency: str


BONGO_STARTER = Offer(
    name="BONGO Starter",
    description="تجربة أولية للوصول إلى خدمات بونجو وحلولها المتكاملة.",
    price="5.00",
    currency="USD",
)
