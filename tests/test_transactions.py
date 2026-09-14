import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
pytestmark = pytest.mark.usefixtures("authenticated_client")


def create_account(balance: int, headers: dict[str, str]) -> dict:
    return client.post(
        "/accounts", json={"balance": balance}, headers=headers
    ).json()


def test_get_transactions_returns_empty_list(authenticated_user):
    account = create_account(0, authenticated_user["headers"])

    response = client.get(f"/accounts/{account['id']}/transactions")

    assert response.status_code == 200
    assert response.json() == []


def test_get_transactions_returns_deposit(authenticated_user):
    account = create_account(0, authenticated_user["headers"])
    client.post(f"/accounts/{account['id']}/deposit", json={"amount": 100})

    response = client.get(f"/accounts/{account['id']}/transactions")

    assert response.status_code == 200
    assert response.json()[0]["type"] == "deposit"
    assert response.json()[0]["amount"] == 100


def test_get_transactions_returns_withdrawal(authenticated_user):
    account = create_account(100, authenticated_user["headers"])
    client.post(f"/accounts/{account['id']}/withdrawals", json={"amount": 40})

    response = client.get(f"/accounts/{account['id']}/transactions")

    assert response.status_code == 200
    assert response.json()[0]["type"] == "withdrawal"
    assert response.json()[0]["amount"] == 40


def test_transfer_transactions_share_reference_id(authenticated_user):
    sender = create_account(100, authenticated_user["headers"])
    recipient = create_account(0, authenticated_user["headers"])
    client.post(
        "/accounts/transfers",
        json={"sender": sender["id"], "recipient": recipient["id"], "amount": 30},
    )

    sender_history = client.get(
        f"/accounts/{sender['id']}/transactions"
    ).json()
    recipient_history = client.get(
        f"/accounts/{recipient['id']}/transactions"
    ).json()

    assert sender_history[0]["type"] == "transfer_out"
    assert recipient_history[0]["type"] == "transfer_in"
    assert sender_history[0]["reference_id"] == recipient_history[0]["reference_id"]


def test_get_transactions_rejects_unknown_account():
    response = client.get("/accounts/999999/transactions")

    assert response.status_code == 404
