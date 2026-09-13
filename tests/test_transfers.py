from fastapi.testclient import TestClient

from app import store
from app.main import app

client = TestClient(app)


def create_account(owner: str, balance: int) -> dict:
    return client.post(
        "/accounts", json={"owner": owner, "balance": balance}
    ).json()


def test_transfer_updates_both_accounts():
    sender = create_account("sender", 100)
    recipient = create_account("recipient", 25)

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


def test_transfer_rejects_unknown_account():
    sender = create_account("known-sender", 100)

    response = client.post(
        "/accounts/transfers",
        json={"sender": sender["id"], "recipient": 999999, "amount": 40},
    )

    assert response.status_code == 404


def test_transfer_rejects_non_positive_amount():
    sender = create_account("valid-sender", 100)
    recipient = create_account("valid-recipient", 0)

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


def test_transfer_rejects_same_account():
    account = create_account("same-account", 100)

    response = client.post(
        "/accounts/transfers",
        json={"sender": account["id"], "recipient": account["id"], "amount": 40},
    )

    assert response.status_code == 409


def test_transfer_rejects_insufficient_funds_without_changing_balances():
    sender = create_account("poor-sender", 25)
    recipient = create_account("safe-recipient", 10)

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
