from fastapi import APIRouter, Depends, HTTPException

from app import services
from app.models import Account, AccountCreate
from app.security import get_current_user

router = APIRouter(prefix="/accounts")


@router.post("", status_code=201, response_model=Account)
async def create_account(
    account: AccountCreate,
    current_user: dict = Depends(get_current_user),
):
    return services.create_account(current_user["id"], account.balance)


@router.get("", response_model=list[Account])
async def get_accounts(current_user: dict = Depends(get_current_user)):
    return services.get_accounts(current_user["id"])


@router.get("/{account_id}", response_model=Account)
async def get_account(
    account_id: int,
    current_user: dict = Depends(get_current_user),
):
    try:
        return services.get_account(current_user["id"], account_id)
    except services.AccountNotFoundError:
        raise HTTPException(status_code=404, detail="Account not found")
