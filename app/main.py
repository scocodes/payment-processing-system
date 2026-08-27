from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "healthy"}

class AccountCreate(BaseModel):
    owner: str = Field(min_length=1)
    opening_balance: int = Field(ge=0)

accounts: dict[int, dict] = {}
next_account_id = 1

@app.post("/accounts", status_code=201)
async def create_account(account: AccountCreate):
        global next_account_id
        new_account = {
            "id" : next_account_id,
            "owner" : account.owner,
            "balance" : accounts.opening_balance
        }
        accounts[next_account_id] = new_account
        next_account_id += 1

        return new_account