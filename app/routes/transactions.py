from fastapi import APIRouter, Depends, HTTPException

from app import services
from app.models import (
    Account,
    DepositCreate,
    Transaction,
    TransferCreate,
    TransferResult,
    WithdrawalCreate,
)
from app.security import get_current_user

router = APIRouter(prefix="/accounts")


@router.get("/{account_id}/transactions", response_model=list[Transaction])
async def get_transactions(
    account_id: int,
    current_user: dict = Depends(get_current_user),
):
    try:
        return services.get_transactions(current_user["id"], account_id)
    except services.AccountNotFoundError:
        raise HTTPException(status_code=404, detail="Account not found")


@router.post("/{account_id}/withdrawals", response_model=Account)
async def withdraw(
    account_id: int,
    withdrawal: WithdrawalCreate,
    current_user: dict = Depends(get_current_user),
):
    try:
        return services.withdraw(current_user["id"], account_id, withdrawal.amount)
    except services.AccountNotFoundError:
        raise HTTPException(status_code=404, detail="Account not found")
    except services.InsufficientFundsError:
        raise HTTPException(status_code=409, detail="Insufficient funds")


@router.post("/{account_id}/deposit", response_model=Account)
async def deposit(
    account_id: int,
    deposit: DepositCreate,
    current_user: dict = Depends(get_current_user),
):
    try:
        return services.deposit(current_user["id"], account_id, deposit.amount)
    except services.AccountNotFoundError:
        raise HTTPException(status_code=404, detail="Account not found")


@router.post("/transfers", response_model=TransferResult)
async def transfers(
    transfer: TransferCreate,
    current_user: dict = Depends(get_current_user),
):
    try:
        return services.transfer(
            current_user["id"],
            transfer.sender,
            transfer.recipient,
            transfer.amount,
        )
    except services.AccountNotFoundError:
        raise HTTPException(status_code=404, detail="Account not found")
    except services.SameAccountError:
        raise HTTPException(status_code=409, detail="Accounts must be different")
    except services.InsufficientFundsError:
        raise HTTPException(status_code=409, detail="Insufficient funds")
