from datetime import datetime
from enum import Enum

from bson import ObjectId
from pydantic import BaseModel, Field

from models.pyobjectid import PyObjectId


class UserRole(str, Enum):
    TRAVELLER = "Traveller"
    TENNO = "Tenno"
    ADMINISTRATOR = "Administrator"


class UserBase(BaseModel):
    email: str
    username: str
    role: UserRole = UserRole.TENNO


class UserCreate(UserBase):
    password: str


class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UserPublic(UserBase):
    id: str
