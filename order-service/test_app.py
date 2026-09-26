import pytest
from unittest.mock import patch, Mock
import app as app_module

app = app_module.app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app_module.ORDERS.clear()
    with app.test_client() as client:
        yield client


def _fake_response(status_code, json_data):
    resp = Mock()
    resp.status_code = status_code
    resp.json.return_value = json_data
    return resp


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "UP"


@patch("app.requests.get")
def test_create_order_success(mock_get, client):
    # First call -> user-service, second call -> product-service
    mock_get.side_effect = [
        _fake_response(200, {"id": 1, "name": "Aarav Shah"}),
        _fake_response(200, {"id": 101, "name": "Wireless Mouse", "price": 599}),
    ]
    resp = client.post("/orders", json={"user_id": 1, "product_id": 101})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["status"] == "CONFIRMED"
    assert body["user"]["name"] == "Aarav Shah"
    assert body["product"]["name"] == "Wireless Mouse"


@patch("app.requests.get")
def test_create_order_user_not_found(mock_get, client):
    mock_get.side_effect = [_fake_response(404, {})]
    resp = client.post("/orders", json={"user_id": 999, "product_id": 101})
    assert resp.status_code == 404


def test_create_order_missing_fields(client):
    resp = client.post("/orders", json={})
    assert resp.status_code == 400


def test_get_orders_empty(client):
    resp = client.get("/orders")
    assert resp.status_code == 200
    assert resp.get_json() == []
