import pytest
from app import app, PRODUCTS


@pytest.fixture
def client():
    app.config["TESTING"] = True
    PRODUCTS.clear()
    with app.test_client() as client:
        yield client


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "UP"


def test_get_products_empty(client):
    resp = client.get("/products")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_product(client):
    resp = client.post("/products", json={"name": "Wireless Mouse", "price": 599})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["name"] == "Wireless Mouse"
    assert "id" in body


def test_create_product_missing_fields(client):
    resp = client.post("/products", json={"name": "Only Name"})
    assert resp.status_code == 400


def test_get_product_found(client):
    created = client.post("/products", json={"name": "Keyboard", "price": 2499}).get_json()
    resp = client.get(f"/products/{created['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Keyboard"


def test_get_product_not_found(client):
    resp = client.get("/products/999")
    assert resp.status_code == 404


def test_update_product(client):
    created = client.post("/products", json={"name": "USB Hub", "price": 999}).get_json()
    resp = client.put(f"/products/{created['id']}", json={"price": 1299})
    assert resp.status_code == 200
    assert resp.get_json()["price"] == 1299


def test_update_product_not_found(client):
    resp = client.put("/products/999", json={"price": 100})
    assert resp.status_code == 404


def test_delete_product(client):
    created = client.post("/products", json={"name": "Temp Item", "price": 1}).get_json()
    resp = client.delete(f"/products/{created['id']}")
    assert resp.status_code == 200
    resp2 = client.get(f"/products/{created['id']}")
    assert resp2.status_code == 404


def test_delete_product_not_found(client):
    resp = client.delete("/products/999")
    assert resp.status_code == 404
