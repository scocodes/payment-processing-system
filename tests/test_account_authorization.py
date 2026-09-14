import pytest
from fastapi.testclient import TestClient

from app import services, store
from app.main import app

client = TestClient(app)


def register_and_login(email: str) -> tuple[dict, dict[str, str]]:
    user = client.post(
        "/users/register",
        json={"email": email, "password": "secret-password"},
    ).json()
    token = client.post(
        "/auth/login",
        json={"email": email, "password": "secret-password"},
    ).json()["access_token"]
    return user, {"Authorization": f"Bearer {token}"}


def test_service_returns_only_owned_accounts():
    owner, _ = register_and_login("owner@example.com")
    stranger, _ = register_and_login("stranger@example.com")
    account = store.create_account(owner["id"], 100)

    assert services.get_accounts(owner["id"]) == [account]
    assert services.get_accounts(stranger["id"]) == []
    with pytest.raises(services.AccountNotFoundError):
        services.get_account(stranger["id"], account["id"])


def test_other_user_cannot_read_account_or_history():
    _, owner_headers = register_and_login("owner@example.com")
    _, stranger_headers = register_and_login("stranger@example.com")
    account = client.post(
        "/accounts", json={"balance": 100}, headers=owner_headers
    ).json()

    assert client.get("/accounts", headers=stranger_headers).json() == []
    assert client.get(f"/accounts/{account['id']}", headers=stranger_headers).status_code == 404
    assert client.get(
        f"/accounts/{account['id']}/transactions", headers=stranger_headers
    ).status_code == 404
    assert client.get("/accounts/999999", headers=stranger_headers).status_code == 404


def test_other_user_cannot_change_balance_or_history():
    _, owner_headers = register_and_login("owner@example.com")
    _, stranger_headers = register_and_login("stranger@example.com")
    account = client.post(
        "/accounts", json={"balance": 100}, headers=owner_headers
    ).json()

    assert client.post(
        f"/accounts/{account['id']}/deposit",
        json={"amount": 25},
        headers=stranger_headers,
    ).status_code == 404
    assert client.post(
        f"/accounts/{account['id']}/withdrawals",
        json={"amount": 25},
        headers=stranger_headers,
    ).status_code == 404

    assert store.get_account(account["id"])["balance"] == 100
    assert store.get_transactions(account["id"]) == []


def test_transfer_requires_sender_ownership_but_allows_other_recipient():
    _, owner_headers = register_and_login("owner@example.com")
    _, stranger_headers = register_and_login("stranger@example.com")
    sender = client.post(
        "/accounts", json={"balance": 100}, headers=owner_headers
    ).json()
    recipient = client.post(
        "/accounts", json={"balance": 10}, headers=stranger_headers
    ).json()
    payload = {"sender": sender["id"], "recipient": recipient["id"], "amount": 25}

    denied = client.post("/accounts/transfers", json=payload, headers=stranger_headers)
    assert denied.status_code == 404
    assert store.get_account(sender["id"])["balance"] == 100
    assert store.get_account(recipient["id"])["balance"] == 10
    assert store.get_transactions() == []

    allowed = client.post("/accounts/transfers", json=payload, headers=owner_headers)
    assert allowed.status_code == 200
    assert allowed.json()["sender"]["balance"] == 75
    assert allowed.json()["recipient"]["balance"] == 35


@pytest.mark.parametrize(
    "method,path,json_body",
    [
        ("get", "/accounts", None),
        ("get", "/accounts/1", None),
        ("get", "/accounts/1/transactions", None),
        ("post", "/accounts/1/deposit", {"amount": 1}),
        ("post", "/accounts/1/withdrawals", {"amount": 1}),
        ("post", "/accounts/transfers", {"sender": 1, "recipient": 2, "amount": 1}),
    ],
)
def test_account_routes_require_token(method, path, json_body):
    response = client.request(method, path, json=json_body)
    assert response.status_code == 401
