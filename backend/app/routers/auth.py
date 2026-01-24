from bson import ObjectId
from database.db import db_manager
from database.dynamic.auth import create_token, decode_token
from database.dynamic.crud import get_user_by_email
from database.dynamic.security import hash_password, verify_password
from fastapi import APIRouter, HTTPException, Request, Response
from models.users import UserCreate, UserPublic, UserRole

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic)
async def register(user: UserCreate):
    # Basic email validation
    if "@" not in user.email or "." not in user.email:
        raise HTTPException(400, "Invalid email format")

    existing_user = await get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(400, "Email already used")

    data = user.model_dump()
    data["hashed_password"] = hash_password(data.pop("password"))
    data["role"] = UserRole.TENNO  # Default role matching UserRole enum

    result = await db_manager.users.insert_one(data)

    return {
        "id": str(result.inserted_id),
        "email": user.email,
        "username": user.username,
        "role": data["role"].value if hasattr(data["role"], "value") else data["role"],
    }


@router.post("/login", response_model=UserPublic)
async def login(data: dict, response: Response):
    user = await db_manager.users.find_one({"email": data.get("email")})
    if not user:
        raise HTTPException(401, "Invalid credentials")

    password = data.get("password")
    if not password or not verify_password(password, user["hashed_password"]):
        raise HTTPException(401, "Invalid credentials")

    token = create_token({"sub": str(user["_id"])})

    response.set_cookie("access_token", token, httponly=True, samesite="lax")

    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "username": user["username"],
        "role": user.get("role", UserRole.TENNO),
    }


@router.get("/me", response_model=UserPublic)
async def me(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(401, "Invalid token")

    except Exception:
        raise HTTPException(status_code=401, detail="Token expired or invalid")

    user = await db_manager.users.find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(status_code=401, detail="Account not found")

    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "username": user["username"],
        "role": user.get("role", UserRole.TENNO),
    }


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}
