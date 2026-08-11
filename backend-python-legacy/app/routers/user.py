from dependencies import get_current_user_id
from fastapi import APIRouter, HTTPException, Request
from models.users import UserPublic
from services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/profile", response_model=UserPublic)
async def get_profile(request: Request):
    user_id = get_current_user_id(request)
    result = await UserService.get_user_by_id(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return result
