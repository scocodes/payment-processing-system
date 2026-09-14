import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
pytestmark = pytest.mark.usefixtures("authenticated_client")


def test_get_accounts_returns_empty_list():
    response = client.get("/accounts")

    assert response.status_code == 200
    assert response.json() == []


def test_get_accounts_returns_all_accounts(authenticated_user):
    first_account = client.post(
        "/accounts", json={"balance": 100}, headers=authenticated_user["headers"]
    ).json()
    second_account = client.post(
        "/accounts", json={"balance": 50}, headers=authenticated_user["headers"]
    ).json()

    response = client.get("/accounts")

    assert response.status_code == 200
    assert response.json() == [first_account, second_account]
