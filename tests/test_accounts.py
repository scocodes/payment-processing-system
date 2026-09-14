import sqlite3

import pytest
from fastapi.testclient import TestClient

from app import store
from app.main import app

client = TestClient(app)


def test_create_account_links_authenticated_user(authenticated_user):
    response = client.post(
        "/accounts",
        json={"balance": 100},
        headers=authenticated_user["headers"],
    )

    assert response.status_code == 201
    account = response.json()
    assert account["user_id"] == authenticated_user["user"]["id"]
    assert account["balance"] == 100
    assert isinstance(account["id"], int)


def test_create_account_requires_token():
    response = client.post("/accounts", json={"balance": 100})

    assert response.status_code == 401


def test_create_account_rejects_missing_balance(authenticated_user):
    response = client.post(
        "/accounts", json={}, headers=authenticated_user["headers"]
    )

    assert response.status_code == 422


def test_create_account_rejects_negative_balance(authenticated_user):
    response = client.post(
        "/accounts",
        json={"balance": -100},
        headers=authenticated_user["headers"],
    )

    assert response.status_code == 422


def test_create_account_ignores_client_supplied_user_id(authenticated_user):
    response = client.post(
        "/accounts",
        json={"user_id": 999999, "balance": 100},
        headers=authenticated_user["headers"],
    )

    assert response.status_code == 201
    assert response.json()["user_id"] == authenticated_user["user"]["id"]


def test_database_rejects_account_for_unknown_user():
    with pytest.raises(sqlite3.IntegrityError):
        store.create_account(999999, 100)


def test_get_account(authenticated_user):
    create_response = client.post(
        "/accounts",
        json={"balance": 25},
        headers=authenticated_user["headers"],
    )
    account = create_response.json()

    response = client.get(f"/accounts/{account['id']}", headers=authenticated_user["headers"])

    assert response.status_code == 200
    assert response.json() == account


def test_get_unknown_account(authenticated_user):
    response = client.get("/accounts/999999", headers=authenticated_user["headers"])

    assert response.status_code == 404
