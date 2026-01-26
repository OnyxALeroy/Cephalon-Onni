from database.db import connect_to_mongodb
from database.dynamic.auth import decode_token
from database.static.age_helper import AgeDB
from fastapi import HTTPException, Request


def get_current_user(request: Request):
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_token(token)
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Token expired or invalid")


def get_age_helper():
    try:
        return AgeDB()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to initialize graph connection: {e}"
        )


def get_static_db_client():
    client = connect_to_mongodb()
    if not client:
        raise HTTPException(status_code=500, detail="Failed to connect to the database")
    yield client
