from typing import Optional

from database.dynamic.auth import create_token
from database.dynamic.security import hash_password, verify_password
from models.users import UserRole
from repositories.user_repository import UserRepository


class AuthService:
    @staticmethod
    async def register(email: str, username: str, password: str) -> dict:
        existing = await UserRepository.find_by_email(email)
        if existing:
            raise ValueError("Email already used")

        user_data = {
            "email": email,
            "username": username,
            "hashed_password": hash_password(password),
            "role": UserRole.TENNO.value,
        }

        user = await UserRepository.create(user_data)
        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "username": user["username"],
            "role": user["role"],
        }

    @staticmethod
    async def login(email: str, password: str) -> dict:
        user = await UserRepository.find_by_email(email)
        if not user:
            raise ValueError("Invalid credentials")

        if not password or not verify_password(password, user["hashed_password"]):
            raise ValueError("Invalid credentials")

        token = create_token({"sub": str(user["_id"])})
        return {
            "token": token,
            "id": str(user["_id"]),
            "email": user["email"],
            "username": user["username"],
            "role": user.get("role", UserRole.TENNO.value),
        }

    @staticmethod
    async def get_current_user(user_id: str) -> Optional[dict]:
        user = await UserRepository.find_by_id(user_id)
        if not user:
            return None
        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "username": user["username"],
            "role": user.get("role", UserRole.TENNO.value),
        }
