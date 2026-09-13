from datetime import datetime, timezone

import jwt
from fastapi.testclient import TestClient

from app.main import app
from app.security import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM

client = TestClient(app)
TEST_SECRET_KEY = "test-secret-key-that-is-not-used-in-production"


def register_user() -> dict:
    return client.post(
        "/users/register",
        json={"email": "scott@example.com", "password": "secret-password"},
    ).json()


def test_login_returns_bearer_token_for_valid_credentials():
    user = register_user()

    response = client.post(
        "/auth/login",
        json={"email": "scott@example.com", "password": "secret-password"},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    payload = jwt.decode(
        response.json()["access_token"], TEST_SECRET_KEY, algorithms=[ALGORITHM]
    )
    assert payload["sub"] == str(user["id"])
    seconds_until_expiry = payload["exp"] - datetime.now(timezone.utc).timestamp()
    assert 0 < seconds_until_expiry <= ACCESS_TOKEN_EXPIRE_MINUTES * 60


def test_login_rejects_wrong_password():
    register_user()

    response = client.post(
        "/auth/login",
        json={"email": "scott@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}
    assert response.headers["www-authenticate"] == "Bearer"


def test_login_rejects_unknown_email_with_same_error():
    response = client.post(
        "/auth/login",
        json={"email": "unknown@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid email or password"}


def test_login_rejects_invalid_request_data():
    response = client.post(
        "/auth/login",
        json={"email": "not-an-email", "password": ""},
    )

    assert response.status_code == 422
