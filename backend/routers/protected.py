from fastapi import APIRouter, Depends

from dependencies import get_current_user

router = APIRouter()

@router.get("/protected")
def protected(user_id: str = Depends(get_current_user)):
    return {"user_id": user_id}
