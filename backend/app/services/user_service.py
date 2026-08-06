from typing import List, Optional

from bson import ObjectId
from database.dynamic.security import hash_password
from models.users import UserRole
from repositories.user_repository import UserRepository


class UserService:
    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[dict]:
        user = await UserRepository.find_by_id(user_id)
        if not user:
            return None
        return {
            "id": str(user["_id"]),
            "email": user["email"],
            "username": user["username"],
            "role": user.get("role", UserRole.TENNO.value),
        }

    @staticmethod
    async def get_all_users() -> List[dict]:
        users = await UserRepository.find_all()
        return [
            {
                "id": str(user["_id"]),
                "email": user["email"],
                "username": user["username"],
                "role": user.get("role", "Tenno"),
            }
            for user in users
        ]

    @staticmethod
    async def update_role(user_id: str, role: UserRole) -> bool:
        return await UserRepository.update_role(user_id, role.value)

    @staticmethod
    async def delete_user(user_id: str) -> bool:
        return await UserRepository.delete(user_id)

    @staticmethod
    async def create_admin(email: str, username: str, password: str) -> dict:
        existing = await UserRepository.find_by_email(email)
        if existing:
            raise ValueError("User with this email already exists")

        admin_data = {
            "email": email,
            "username": username,
            "hashed_password": hash_password(password),
            "role": UserRole.ADMINISTRATOR.value,
        }

        user = await UserRepository.create(admin_data)
        return {
            "id": str(user["_id"]),
            "email": email,
            "username": username,
            "role": UserRole.ADMINISTRATOR.value,
        }
