from fastapi import APIRouter, HTTPException

from app import store
from app.models import (
    Account,
    DepositCreate,
    Transaction,
    TransferCreate,
    TransferResult,
    WithdrawalCreate,
)

router = APIRouter(prefix="/accounts")


@router.get("/{account_id}/transactions", response_model=list[Transaction])
async def get_transactions(account_id: int):
    if store.get_account(account_id) is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return store.get_transactions(account_id)


@router.post("/{account_id}/withdrawals", response_model=Account)
async def withdraw(account_id: int, withdrawal: WithdrawalCreate):
    try:
        return store.withdraw(account_id, withdrawal.amount)
    except store.AccountNotFoundError:
        raise HTTPException(status_code=404, detail="Account not found")
    except store.InsufficientFundsError:
        raise HTTPException(status_code=409, detail="Insufficient funds")


@router.post("/{account_id}/deposit", response_model=Account)
async def deposit(account_id: int, deposit: DepositCreate):
    try:
        return store.deposit(account_id, deposit.amount)
    except store.AccountNotFoundError:
        raise HTTPException(status_code=404, detail="Account not found")


@router.post("/transfers", response_model=TransferResult)
async def transfers(transfer: TransferCreate):
    try:
        return store.transfer(transfer.sender, transfer.recipient, transfer.amount)
    except store.AccountNotFoundError:
        raise HTTPException(status_code=404, detail="Account not found")
    except store.SameAccountError:
        raise HTTPException(status_code=409, detail="Accounts must be different")
    except store.InsufficientFundsError:
        raise HTTPException(status_code=409, detail="Insufficient funds")
