from fastapi import APIRouter, HTTPException

from app import store
from app.models import Account, AccountCreate

router = APIRouter(prefix="/accounts")


@router.post("", status_code=201, response_model=Account)
async def create_account(account: AccountCreate):
    return store.create_account(account.owner, account.balance)


@router.get("", response_model=list[Account])
async def get_accounts():
    return store.get_accounts()


@router.get("/{account_id}", response_model=Account)
async def get_account(account_id: int):
    account = store.get_account(account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account
