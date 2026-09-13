from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class User(BaseModel):
    id: int
    email: EmailStr
    created_at: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class Token(BaseModel):
    access_token: str
    token_type: str


class AccountCreate(BaseModel):
    owner: str = Field(min_length=1)
    balance: int = Field(ge=0)


class Account(BaseModel):
    id: int
    owner: str
    balance: int


class WithdrawalCreate(BaseModel):
    amount: int = Field(gt=0)


class DepositCreate(BaseModel):
    amount: int = Field(gt=0)


class TransferCreate(BaseModel):
    amount: int = Field(gt=0)
    sender: int = Field(gt=0)
    recipient: int = Field(gt=0)


class Transaction(BaseModel):
    id: int
    account_id: int
    type: str
    amount: int
    reference_id: str | None
    created_at: str


class TransferResult(BaseModel):
    sender: Account
    recipient: Account
