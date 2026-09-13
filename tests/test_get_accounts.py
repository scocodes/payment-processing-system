from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_get_accounts_returns_empty_list():
    response = client.get("/accounts")

    assert response.status_code == 200
    assert response.json() == []


def test_get_accounts_returns_all_accounts():
    first_account = client.post(
        "/accounts", json={"owner": "first", "balance": 100}
    ).json()
    second_account = client.post(
        "/accounts", json={"owner": "second", "balance": 50}
    ).json()

    response = client.get("/accounts")

    assert response.status_code == 200
    assert response.json() == [first_account, second_account]
