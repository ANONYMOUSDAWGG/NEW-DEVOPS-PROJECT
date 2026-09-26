import pytest
from app import app, USERS


@pytest.fixture
def client():
    app.config["TESTING"] = True
    USERS.clear()
    with app.test_client() as client:
        yield client


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "UP"


def test_get_users_empty(client):
    resp = client.get("/users")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_user(client):
    resp = client.post("/users", json={"name": "Aarav Shah", "email": "aarav@example.com"})
    assert resp.status_code == 201
    body = resp.get_json()
    assert body["name"] == "Aarav Shah"
    assert "id" in body


def test_create_user_missing_fields(client):
    resp = client.post("/users", json={"name": "Only Name"})
    assert resp.status_code == 400


def test_get_user_found(client):
    created = client.post("/users", json={"name": "Priya Mehta", "email": "priya@example.com"}).get_json()
    resp = client.get(f"/users/{created['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Priya Mehta"


def test_get_user_not_found(client):
    resp = client.get("/users/999")
    assert resp.status_code == 404


def test_update_user(client):
    created = client.post("/users", json={"name": "Rohan", "email": "rohan@example.com"}).get_json()
    resp = client.put(f"/users/{created['id']}", json={"name": "Rohan Kulkarni"})
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Rohan Kulkarni"


def test_update_user_not_found(client):
    resp = client.put("/users/999", json={"name": "Nobody"})
    assert resp.status_code == 404


def test_delete_user(client):
    created = client.post("/users", json={"name": "Temp User", "email": "temp@example.com"}).get_json()
    resp = client.delete(f"/users/{created['id']}")
    assert resp.status_code == 200
    resp2 = client.get(f"/users/{created['id']}")
    assert resp2.status_code == 404


def test_delete_user_not_found(client):
    resp = client.delete("/users/999")
    assert resp.status_code == 404
