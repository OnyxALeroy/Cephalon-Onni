from typing import List, Optional

from dependencies import get_current_admin_user
from fastapi import APIRouter, Depends, HTTPException
from models.users import UserPublic, UserRole
from services.user_service import UserService

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/users", response_model=List[UserPublic])
async def get_all_users(
    search: Optional[str] = None, current_admin: dict = Depends(get_current_admin_user)
):
    return await UserService.get_all_users()


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str, role: UserRole, current_admin: dict = Depends(get_current_admin_user)
):
    if str(current_admin["_id"]) == user_id:
        raise HTTPException(400, "Cannot modify your own role")

    if role not in UserRole:
        raise HTTPException(400, "Invalid role")

    from bson import ObjectId

    try:
        ObjectId(user_id)
    except ValueError:
        raise HTTPException(400, "Invalid user ID")

    user = await UserService.get_user_by_id(user_id)
    if not user:
        raise HTTPException(404, "User not found")

    updated = await UserService.update_role(user_id, role)
    if not updated:
        raise HTTPException(500, "Failed to update user role")

    return {"message": f"User role updated to {role}"}


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str, current_admin: dict = Depends(get_current_admin_user)
):
    if str(current_admin["_id"]) == user_id:
        raise HTTPException(400, "Cannot delete your own account")

    from bson import ObjectId

    try:
        ObjectId(user_id)
    except ValueError:
        raise HTTPException(400, "Invalid user ID")

    deleted = await UserService.delete_user(user_id)
    if not deleted:
        raise HTTPException(404, "User not found")

    return {"message": "User deleted successfully"}


@router.post("/create-admin")
async def create_admin_user(
    email: str,
    username: str,
    password: str,
    current_admin: dict = Depends(get_current_admin_user),
):
    try:
        result = await UserService.create_admin(email, username, password)
    except ValueError as e:
        raise HTTPException(400, str(e))

    return result
