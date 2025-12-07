from bson import ObjectId
from fastapi import APIRouter, HTTPException, Response, Request

from models.users import UserCreate, UserPublic
from database.dynamic.auth import create_token, decode_token
from database.dynamic.crud import create_user, get_user_by_email
from database.dynamic.security import hash_password, verify_password
from database.dynamic.db import users_collection

router = APIRouter()

@router.post("/register", response_model=UserPublic)
def register(user: UserCreate):
    if get_user_by_email(user.email):
        raise HTTPException(400, "Email already used")

    data = user.dict()
    data["hashed_password"] = hash_password(data.pop("password"))

    result = users_collection.insert_one(data)

    return {
        "id": str(result.inserted_id),
        "email": user.email,
        "username": user.username
    }


@router.post("/login", response_model=UserPublic)
def login(data: dict, response: Response):
    user = users_collection.find_one({"email": data.get("email")})
    if not user:
        raise HTTPException(401, "Invalid credentials")

    if not verify_password(data.get("password"), user["hashed_password"]):
        raise HTTPException(401, "Invalid credentials")

    token = create_token(str(user["_id"]))

    response.set_cookie(
        "access_token",
        token,
        httponly=True,
        samesite="lax"
    )

    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "username": user["username"]
    }

@router.get("/me", response_model=UserPublic)
def me(request: Request):
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

    user = users_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(status_code=401, detail="Account not found")

    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "username": user["username"]
    }
