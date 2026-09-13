from datetime import datetime, timedelta, timezone

import jwt
from fastapi.testclient import TestClient

from app.main import app
from app.security import ALGORITHM

client = TestClient(app)
TEST_SECRET_KEY = "test-secret-key-that-is-not-used-in-production"


def register_and_login() -> tuple[dict, str]:
    user = client.post(
        "/users/register",
        json={"email": "scott@example.com", "password": "secret-password"},
    ).json()
    token = client.post(
        "/auth/login",
        json={"email": "scott@example.com", "password": "secret-password"},
    ).json()["access_token"]
    return user, token


def authorization_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_get_current_user_with_valid_token():
    user, token = register_and_login()

    response = client.get("/users/me", headers=authorization_header(token))

    assert response.status_code == 200
    assert response.json() == user


def test_get_current_user_rejects_missing_token():
    response = client.get("/users/me")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_get_current_user_rejects_altered_token():
    _, token = register_and_login()

    response = client.get(
        "/users/me", headers=authorization_header(f"{token}altered")
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


def test_get_current_user_rejects_expired_token():
    user, _ = register_and_login()
    expired_token = jwt.encode(
        {
            "sub": str(user["id"]),
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        TEST_SECRET_KEY,
        algorithm=ALGORITHM,
    )

    response = client.get(
        "/users/me", headers=authorization_header(expired_token)
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


def test_get_current_user_rejects_token_for_unknown_user():
    token = jwt.encode(
        {
            "sub": "999999",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=1),
        },
        TEST_SECRET_KEY,
        algorithm=ALGORITHM,
    )

    response = client.get("/users/me", headers=authorization_header(token))

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}
