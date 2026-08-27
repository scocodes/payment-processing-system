from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "healthy"}

class AccountCreate(BaseModel):
    owner: str = Field(min_length=1)
    balance: int = Field(ge=0)

class WithdrawalCreate(BaseModel):
    amount: int = Field(gt=0)

accounts: dict[int, dict] = {}
next_account_id = 1

@app.post("/accounts", status_code=201)
async def create_account(account: AccountCreate):
        global next_account_id
        new_account = {
            "id" : next_account_id,
            "owner" : account.owner,
            "balance" : account.balance
        }
        accounts[next_account_id] = new_account
        next_account_id += 1

        return new_account

@app.get("/accounts/{account_id}")
async def get_account(account_id: int):
        account = accounts.get(account_id)
        if account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        return account

@app.post("/accounts/{account_id}/withdrawals")
async def withdraw(account_id: int, withdrawal: WithdrawalCreate):
        account = accounts.get(account_id)
        if account is None:
            raise HTTPException(status_code=404, detail="Account not found")
        if withdrawal.amount > account["balance"]:
            raise HTTPException(status_code=409, detail="Insufficient funds")

        account["balance"] -= withdrawal.amount
        return account
