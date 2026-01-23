from typing import List

from bson import ObjectId
from database.db import db_manager
from database.dynamic.auth import decode_token
from database.dynamic.security import hash_password
from fastapi import APIRouter, Depends, HTTPException, Request
from models.users import UserPublic, UserRole

router = APIRouter(prefix="/api/admin", tags=["admin"])


async def get_current_admin_user(request: Request):
    """Dependency to verify current user is an administrator"""
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(401, detail="Invalid token")

    except Exception:
        raise HTTPException(status_code=401, detail="Token expired or invalid")

    user = await db_manager.users.find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(status_code=401, detail="Account not found")

    if user.get("role") != "Administrator":
        raise HTTPException(status_code=403, detail="Administrator access required")

    return user


@router.get("/users", response_model=List[UserPublic])
async def get_all_users(current_admin: dict = Depends(get_current_admin_user)):
    """Get all users (admin only)"""
    users = []
    cursor = db_manager.users.find({})

    async for user in cursor:
        users.append(
            {
                "id": str(user["_id"]),
                "email": user["email"],
                "username": user["username"],
                "role": user.get("role", "Tenno"),
            }
        )

    return users


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str, role: UserRole, current_admin: dict = Depends(get_current_admin_user)
):
    """Update a user's role (admin only)"""
    # Prevent admins from demoting themselves
    if str(current_admin["_id"]) == user_id:
        raise HTTPException(400, "Cannot modify your own role")

    # Validate the role
    if role not in UserRole:
        raise HTTPException(400, "Invalid role")

    # Check if user exists
    try:
        object_id = ObjectId(user_id)
    except ValueError:
        raise HTTPException(400, "Invalid user ID")

    user = await db_manager.users.find_one({"_id": object_id})
    if not user:
        raise HTTPException(404, "User not found")

    # Update the user's role
    result = await db_manager.users.update_one(
        {"_id": object_id}, {"$set": {"role": role}}
    )

    if result.modified_count == 0:
        raise HTTPException(500, "Failed to update user role")

    return {"message": f"User role updated to {role}"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str, current_admin: dict = Depends(get_current_admin_user)
):
    """Delete a user (admin only)"""
    # Prevent admins from deleting themselves
    if str(current_admin["_id"]) == user_id:
        raise HTTPException(400, "Cannot delete your own account")

    try:
        object_id = ObjectId(user_id)
    except ValueError:
        raise HTTPException(400, "Invalid user ID")

    result = await db_manager.users.delete_one({"_id": object_id})

    if result.deleted_count == 0:
        raise HTTPException(404, "User not found")

    return {"message": "User deleted successfully"}


@router.post("/create-admin")
async def create_admin_user(
    email: str,
    username: str,
    password: str,
    current_admin: dict = Depends(get_current_admin_user),
):
    """Create a new administrator user (admin only)"""
    # Check if user already exists
    existing_user = await db_manager.users.find_one({"email": email})
    if existing_user:
        raise HTTPException(400, "User with this email already exists")

    # Create new admin user
    admin_user = {
        "email": email,
        "username": username,
        "hashed_password": hash_password(password),
        "role": UserRole.ADMINISTRATOR,
    }

    result = await db_manager.users.insert_one(admin_user)

    return {
        "id": str(result.inserted_id),
        "email": email,
        "username": username,
        "role": UserRole.ADMINISTRATOR,
    }
