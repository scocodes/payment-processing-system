from fastapi.testclient import TestClient

from app import store
from app.main import app

client = TestClient(app)


def test_withdrawal_updates_account(authenticated_user):
    account = client.post(
        "/accounts", json={"balance": 100}, headers=authenticated_user["headers"]
    ).json()

    response = client.post(
        f"/accounts/{account['id']}/withdrawals", json={"amount": 40}
    )

    assert response.status_code == 200
    assert response.json()["balance"] == 60
    transactions = store.get_transactions(account["id"])
    assert len(transactions) == 1
    assert transactions[0]["type"] == "withdrawal"
    assert transactions[0]["amount"] == 40


def test_withdrawal_rejects_unknown_account():
    response = client.post("/accounts/999999/withdrawals", json={"amount": 10})

    assert response.status_code == 404


def test_withdrawal_rejects_non_positive_amount(authenticated_user):
    account = client.post(
        "/accounts", json={"balance": 100}, headers=authenticated_user["headers"]
    ).json()

    for amount in (0, -1):
        response = client.post(
            f"/accounts/{account['id']}/withdrawals", json={"amount": amount}
        )

        assert response.status_code == 422


def test_withdrawal_rejects_insufficient_funds_without_changing_balance(
    authenticated_user,
):
    account = client.post(
        "/accounts", json={"balance": 25}, headers=authenticated_user["headers"]
    ).json()

    response = client.post(
        f"/accounts/{account['id']}/withdrawals", json={"amount": 30}
    )
    stored_account = client.get(f"/accounts/{account['id']}").json()

    assert response.status_code == 409
    assert stored_account["balance"] == 25
    assert store.get_transactions(account["id"]) == []
