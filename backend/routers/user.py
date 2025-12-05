from fastapi import APIRouter, HTTPException

from backend.models.users import UserCreate
from backend.database.dynamic.auth import create_token
from backend.database.dynamic.crud import create_user, get_user_by_email
from backend.database.dynamic.security import verify_password

router = APIRouter()

@router.post("/register")
async def register(user: UserCreate):
    try:
        u = await create_user(user)
        return {"message": "User created"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(email: str, password: str):
    user = await get_user_by_email(email)

    if not user or not verify_password(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"sub": str(user["_id"])})
    return {"access_token": token}
