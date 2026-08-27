from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_account_bal():
    response = client.post("/accounts", json={"owner": "sco", "balance" : 100})

    assert response.status_code == 201
    account = response.json()

    assert account["owner"] == "sco"
    assert account["balance"] == 100
    assert isinstance(account["id"], int)

def test_create_account_rejects_empty_owner():

    response = client.post("/accounts", json={"owner": ""})

    assert response.status_code == 422

def test_create_account_rejects_missing_owner():

    response = client.post("/accounts", json={})

    assert response.status_code == 422

def test_negative_account_balance():

    response = client.post("/accounts", json={"owner" : "sco", "balance" : -100})

    assert response.status_code == 422

def test_get_account():
    create_response = client.post(
        "/accounts", json={"owner": "retrievable", "balance": 25}
    )
    account = create_response.json()

    response = client.get(f"/accounts/{account['id']}")

    assert response.status_code == 200
    assert response.json() == account

def test_get_unknown_account():
    response = client.get("/accounts/999999")

    assert response.status_code == 404
