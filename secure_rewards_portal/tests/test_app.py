from fastapi.testclient import TestClient
from secure_rewards_portal.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_landing_page_never_requests_card_data():
    response = client.get("/")
    assert response.status_code == 200
    assert "CVV" in response.text
    assert 'name="card_number"' not in response.text
    assert 'id="cvv"' not in response.text


def test_checkout_is_disabled_without_provider(monkeypatch):
    monkeypatch.setattr("secure_rewards_portal.main.CHECKOUT_URL", "")
    response = client.post(
        "/api/v1/checkout",
        json={"full_name": "Test User", "email": "test@example.com"},
    )
    assert response.status_code == 503


def test_security_headers():
    response = client.get("/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["cache-control"] == "no-store"
