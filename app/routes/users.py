from fastapi import APIRouter, Depends, HTTPException

from app import store
from app.models import User, UserCreate
from app.security import get_current_user, hash_password

router = APIRouter(prefix="/users")


@router.get("/me", response_model=User)
async def read_current_user(current_user: dict = Depends(get_current_user)):
    return current_user


@router.post("/register", status_code=201, response_model=User)
async def register_user(user: UserCreate):
    hashed_password = hash_password(user.password)
    try:
        return store.create_user(str(user.email), hashed_password)
    except store.UserAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Email already registered")
