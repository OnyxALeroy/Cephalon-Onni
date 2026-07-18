from database.db import connect_to_mongodb
from database.dynamic.auth import decode_token
from database.postgres_db import postgres_db
from fastapi import HTTPException, Request


def get_current_user_id(request: Request) -> str:
    """Extract user_id from JWT token — single source of truth."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Token expired or invalid")


async def get_current_user(request: Request) -> dict:
    """Fetch full user document for the current session."""
    from repositories.user_repository import UserRepository

    user_id = get_current_user_id(request)
    user = await UserRepository.find_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Account not found")
    return user


async def get_current_admin_user(request: Request) -> dict:
    """Fetch current user and verify Administrator role."""
    user = await get_current_user(request)
    if user.get("role") != "Administrator":
        raise HTTPException(status_code=403, detail="Administrator access required")
    return user


def get_static_db_client():
    client = connect_to_mongodb()
    if not client:
        raise HTTPException(status_code=500, detail="Failed to connect to the database")
    yield client


async def get_postgres_session():
    async for session in postgres_db.get_session():
        yield session


def get_age_helper():
    from database.static.age_helper import AgeDB

    age = AgeDB()
    try:
        yield age
    finally:
        age.close()
