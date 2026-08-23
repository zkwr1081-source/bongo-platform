from .status import PaymentStatus


def verify_payment(payment_status: PaymentStatus) -> bool:
    return payment_status == PaymentStatus.PAID


def can_deliver_service(payment_status: PaymentStatus) -> bool:
    return verify_payment(payment_status)
