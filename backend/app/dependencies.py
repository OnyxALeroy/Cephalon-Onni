from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from routers.user import decode_token

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2)):
    try:
        data = decode_token(token)
        return data["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
