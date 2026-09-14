from app import store


class AccountNotFoundError(Exception):
    pass


InsufficientFundsError = store.InsufficientFundsError
SameAccountError = store.SameAccountError


def create_account(user_id: int, balance: int) -> dict:
    return store.create_account(user_id, balance)


def get_account(user_id: int, account_id: int) -> dict:
    account = store.get_account(account_id, user_id)
    if account is None:
        raise AccountNotFoundError
    return account


def get_accounts(user_id: int) -> list[dict]:
    return store.get_accounts(user_id)


def get_transactions(user_id: int, account_id: int) -> list[dict]:
    get_account(user_id, account_id)
    return store.get_transactions(account_id)


def deposit(user_id: int, account_id: int, amount: int) -> dict:
    get_account(user_id, account_id)
    try:
        return store.deposit(account_id, amount, user_id)
    except store.AccountNotFoundError:
        raise AccountNotFoundError from None


def withdraw(user_id: int, account_id: int, amount: int) -> dict:
    get_account(user_id, account_id)
    try:
        return store.withdraw(account_id, amount, user_id)
    except store.AccountNotFoundError:
        raise AccountNotFoundError from None


def transfer(user_id: int, sender_id: int, recipient_id: int, amount: int) -> dict:
    get_account(user_id, sender_id)
    try:
        return store.transfer(sender_id, recipient_id, amount, user_id)
    except store.AccountNotFoundError:
        raise AccountNotFoundError from None
