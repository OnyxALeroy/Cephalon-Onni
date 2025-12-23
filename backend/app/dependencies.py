from fastapi import Depends, HTTPException, Request
from database.dynamic.auth import decode_token

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
