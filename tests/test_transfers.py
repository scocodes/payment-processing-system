import pytest
from fastapi.testclient import TestClient

from app import store
from app.main import app

client = TestClient(app)
pytestmark = pytest.mark.usefixtures("authenticated_client")


def create_account(balance: int, headers: dict[str, str]) -> dict:
    return client.post(
        "/accounts", json={"balance": balance}, headers=headers
    ).json()


def test_transfer_updates_both_accounts(authenticated_user):
    sender = create_account(100, authenticated_user["headers"])
    recipient = create_account(25, authenticated_user["headers"])

    response = client.post(
        "/accounts/transfers",
        json={"sender": sender["id"], "recipient": recipient["id"], "amount": 40},
    )

    assert response.status_code == 200
    assert response.json()["sender"]["balance"] == 60
    assert response.json()["recipient"]["balance"] == 65
    transactions = store.get_transactions()
    assert [transaction["type"] for transaction in transactions] == [
        "transfer_out",
        "transfer_in",
    ]
    assert [transaction["account_id"] for transaction in transactions] == [
        sender["id"],
        recipient["id"],
    ]
    assert all(transaction["amount"] == 40 for transaction in transactions)
    assert transactions[0]["reference_id"] == transactions[1]["reference_id"]
    assert transactions[0]["reference_id"] is not None


def test_transfer_rejects_unknown_account(authenticated_user):
    sender = create_account(100, authenticated_user["headers"])

    response = client.post(
        "/accounts/transfers",
        json={"sender": sender["id"], "recipient": 999999, "amount": 40},
    )

    assert response.status_code == 404


def test_transfer_rejects_non_positive_amount(authenticated_user):
    sender = create_account(100, authenticated_user["headers"])
    recipient = create_account(0, authenticated_user["headers"])

    for amount in (0, -1):
        response = client.post(
            "/accounts/transfers",
            json={
                "sender": sender["id"],
                "recipient": recipient["id"],
                "amount": amount,
            },
        )

        assert response.status_code == 422


def test_transfer_rejects_same_account(authenticated_user):
    account = create_account(100, authenticated_user["headers"])

    response = client.post(
        "/accounts/transfers",
        json={"sender": account["id"], "recipient": account["id"], "amount": 40},
    )

    assert response.status_code == 409


def test_transfer_rejects_insufficient_funds_without_changing_balances(
    authenticated_user,
):
    sender = create_account(25, authenticated_user["headers"])
    recipient = create_account(10, authenticated_user["headers"])

    response = client.post(
        "/accounts/transfers",
        json={"sender": sender["id"], "recipient": recipient["id"], "amount": 30},
    )
    stored_sender = client.get(f"/accounts/{sender['id']}").json()
    stored_recipient = client.get(f"/accounts/{recipient['id']}").json()

    assert response.status_code == 409
    assert stored_sender["balance"] == 25
    assert stored_recipient["balance"] == 10
    assert store.get_transactions() == []
