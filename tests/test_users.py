from fastapi.testclient import TestClient

from app import store
from app.main import app
from app.security import verify_password

client = TestClient(app)


def test_register_user_stores_hashed_password_and_returns_safe_user():
    response = client.post(
        "/users/register",
        json={"email": "scott@example.com", "password": "secret-password"},
    )

    assert response.status_code == 201
    assert response.json()["email"] == "scott@example.com"
    assert "password" not in response.json()
    assert "password_hash" not in response.json()

    stored_user = store.get_user_by_email("scott@example.com")
    assert stored_user["password_hash"] != "secret-password"
    assert verify_password("secret-password", stored_user["password_hash"])


def test_register_user_rejects_invalid_email():
    response = client.post(
        "/users/register",
        json={"email": "not-an-email", "password": "secret-password"},
    )

    assert response.status_code == 422


def test_register_user_rejects_short_password():
    response = client.post(
        "/users/register",
        json={"email": "scott@example.com", "password": "short"},
    )

    assert response.status_code == 422


def test_register_user_rejects_missing_fields():
    response = client.post("/users/register", json={})

    assert response.status_code == 422


def test_register_user_rejects_duplicate_email():
    user = {"email": "scott@example.com", "password": "secret-password"}
    first_response = client.post("/users/register", json=user)
    duplicate_response = client.post("/users/register", json=user)

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409
    assert duplicate_response.json() == {"detail": "Email already registered"}
