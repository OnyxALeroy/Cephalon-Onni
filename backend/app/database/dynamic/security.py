from passlib.context import CryptContext

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_ctx.hash(password)

def verify_password(password: str, h: str) -> bool:
    return pwd_ctx.verify(password, h)
