from fastapi.testclient import TestClient

from app import store
from app.main import app

client = TestClient(app)


def test_deposit_updates_account():
    account = client.post("/accounts", json={"owner": "depositor", "balance": 0}).json()

    response = client.post(f"/accounts/{account['id']}/deposit", json={"amount": 100})

    assert response.status_code == 200
    assert response.json()["balance"] == 100
    transactions = store.get_transactions(account["id"])
    assert len(transactions) == 1
    assert transactions[0]["type"] == "deposit"
    assert transactions[0]["amount"] == 100


def test_deposit_rejects_unknown_account():
    response = client.post("/accounts/999999/deposit", json={"amount": 100})

    assert response.status_code == 404


def test_deposit_rejects_non_positive_amount():
    account = client.post(
        "/accounts", json={"owner": "deposit-validator", "balance": 0}
    ).json()

    for amount in (0, -1):
        response = client.post(
            f"/accounts/{account['id']}/deposit", json={"amount": amount}
        )

        assert response.status_code == 422

    assert store.get_transactions(account["id"]) == []
