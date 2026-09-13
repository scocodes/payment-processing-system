from fastapi import APIRouter, HTTPException

from app import store
from app.models import LoginRequest, Token
from app.security import DUMMY_PASSWORD_HASH, create_access_token, verify_password

router = APIRouter(prefix="/auth")


def authenticate_user(email: str, password: str) -> dict | None:
    user = store.get_user_by_email(email)
    if user is None:
        verify_password(password, DUMMY_PASSWORD_HASH)
        return None
    if not verify_password(password, user["password_hash"]):
        return None
    return user


@router.post("/login", response_model=Token)
async def login(login_request: LoginRequest):
    user = authenticate_user(str(login_request.email), login_request.password)
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "access_token": create_access_token(user["id"]),
        "token_type": "bearer",
    }
