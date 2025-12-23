from fastapi import APIRouter, Depends, Request

from dependencies import get_current_user

router = APIRouter()

@router.get("/protected")
def protected(request: Request, user_id: str = Depends(get_current_user)):
    return {"user_id": user_id}
