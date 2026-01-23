from bson import ObjectId
from database.db import db_manager
from database.dynamic.auth import decode_token
from fastapi import APIRouter, HTTPException, Request
from models.users import UserPublic, UserRole

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/profile", response_model=UserPublic)
async def get_profile(request: Request):
    """Get current user profile"""
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
