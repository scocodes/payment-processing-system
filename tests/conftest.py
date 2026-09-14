import pytest
from fastapi.testclient import TestClient

from app import store
from app.main import app


@pytest.fixture(autouse=True)
def empty_account_store(monkeypatch, tmp_path):
    monkeypatch.setattr(store, "DATABASE_PATH", tmp_path / "accounts.db")
    monkeypatch.setenv("SECRET_KEY", "test-secret-key-that-is-not-used-in-production")
    store.initialize_database()


@pytest.fixture
def authenticated_user():
    client = TestClient(app)
    user = client.post(
        "/users/register",
        json={"email": "account-owner@example.com", "password": "secret-password"},
    ).json()
    token = client.post(
        "/auth/login",
        json={"email": "account-owner@example.com", "password": "secret-password"},
    ).json()["access_token"]
    return {
        "user": user,
        "headers": {"Authorization": f"Bearer {token}"},
    }


@pytest.fixture
def authenticated_client(request, authenticated_user):
    client = request.module.client
    original_headers = client.headers.copy()
    client.headers.update(authenticated_user["headers"])
    yield
    client.headers.clear()
    client.headers.update(original_headers)
