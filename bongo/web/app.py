from fastapi import FastAPI, HTTPException
from bongo.api.services import public_services, public_service
from bongo.api.customer import prepare_service_order

app = FastAPI(
    title="BONGO",
    description="بونجو — ممر الحلول المتكامل",
    version="1.2.0",
)


@app.get("/")
def home():
    return {
        "name": "BONGO",
        "description": "ممر الحلول المتكامل",
        "status": "online"
    }


@app.get("/api/services")
def services():
    return {
        "services": public_services()
    }


@app.get("/api/services/{service_id}")
def service(service_id: str):
    result = public_service(service_id)

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )

    return result


@app.post("/api/services/{service_id}/order")
def create_order(service_id: str):
    try:
        order = prepare_service_order(service_id)

        return {
            "order_id": order.order_id,
            "service_id": order.offer_id,
            "amount": order.amount,
            "currency": order.currency,
            "payment_status": order.payment_status.value,
            "message": "Order created. Payment provider is not connected yet."
        }

    except ValueError:
        raise HTTPException(
            status_code=404,
            detail="Service not found"
        )
