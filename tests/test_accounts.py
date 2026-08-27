from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_account_bal():
    response = client.post("/accounts", json={"owner": "sco", "opening_balance" : 100})

    assert response.status_code == 201
    account = response.json()

    assert account["owner"] == "sco"
    assert account["opening_balance"] == 100
    assert isinstance(account["id"], int)

def test_create_account_rejects_empty_owner():

    response = client.post("/accounts", json={"owner": ""})

    assert response.status_code == 422

def test_create_account_rejects_missing_owner():

    response = client.post("/accounts", json={})

    assert response.status_code == 422

def test_negative_account_balance():

    response = client.post("/accounts", json={"owner" : "sco", "opening_balance:" : -100})

    assert response.status_code == 422


                        