from fastapi import FastAPI

from app.routes.accounts import router as accounts_router
from app.routes.auth import router as auth_router
from app.routes.transactions import router as transactions_router
from app.routes.users import router as users_router

app = FastAPI()
app.include_router(accounts_router)
app.include_router(auth_router)
app.include_router(transactions_router)
app.include_router(users_router)


@app.get("/health")
async def health():
    return {"status": "healthy"}
