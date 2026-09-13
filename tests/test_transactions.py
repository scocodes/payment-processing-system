from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def create_account(owner: str, balance: int) -> dict:
    return client.post(
        "/accounts", json={"owner": owner, "balance": balance}
    ).json()


def test_get_transactions_returns_empty_list():
    account = create_account("no-activity", 0)

    response = client.get(f"/accounts/{account['id']}/transactions")

    assert response.status_code == 200
    assert response.json() == []


def test_get_transactions_returns_deposit():
    account = create_account("depositor", 0)
    client.post(f"/accounts/{account['id']}/deposit", json={"amount": 100})

    response = client.get(f"/accounts/{account['id']}/transactions")

    assert response.status_code == 200
    assert response.json()[0]["type"] == "deposit"
    assert response.json()[0]["amount"] == 100


def test_get_transactions_returns_withdrawal():
    account = create_account("withdrawer", 100)
    client.post(f"/accounts/{account['id']}/withdrawals", json={"amount": 40})

    response = client.get(f"/accounts/{account['id']}/transactions")

    assert response.status_code == 200
    assert response.json()[0]["type"] == "withdrawal"
    assert response.json()[0]["amount"] == 40


def test_transfer_transactions_share_reference_id():
    sender = create_account("sender", 100)
    recipient = create_account("recipient", 0)
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
