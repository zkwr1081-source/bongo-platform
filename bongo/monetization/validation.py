from decimal import Decimal, InvalidOperation


def validate_offer(offer):
    if not offer:
        raise ValueError("Offer not found")

    if not offer.get("name"):
        raise ValueError("Offer name is required")

    if not offer.get("currency"):
        raise ValueError("Offer currency is required")

    try:
        price = Decimal(offer.get("price", "0"))
    except (InvalidOperation, TypeError):
        raise ValueError("Invalid price")

    if price <= 0:
        raise ValueError("Price must be greater than zero")

    return True
