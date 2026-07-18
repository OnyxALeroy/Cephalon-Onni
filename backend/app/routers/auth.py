from dependencies import get_current_user_id
from fastapi import APIRouter, HTTPException, Request, Response
from models.users import UserCreate, UserPublic
from services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic)
async def register(user: UserCreate):
    if "@" not in user.email or "." not in user.email:
        raise HTTPException(400, "Invalid email format")

    try:
        result = await AuthService.register(user.email, user.username, user.password)
    except ValueError as e:
        raise HTTPException(400, str(e))

    return result


@router.post("/login", response_model=UserPublic)
async def login(data: dict, response: Response):
    try:
        result = await AuthService.login(data.get("email", ""), data.get("password", ""))
    except ValueError as e:
        raise HTTPException(401, str(e))

    response.set_cookie("access_token", result["token"], httponly=True, samesite="lax")
    return {
        "id": result["id"],
        "email": result["email"],
        "username": result["username"],
        "role": result["role"],
    }


@router.get("/me", response_model=UserPublic)
async def me(request: Request):
    user_id = get_current_user_id(request)

    result = await AuthService.get_current_user(user_id)
    if not result:
        raise HTTPException(status_code=401, detail="Account not found")

    return result


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out successfully"}
