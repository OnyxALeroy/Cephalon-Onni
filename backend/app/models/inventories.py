from typing import Optional, List, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId
from models.pyobjectid import PyObjectId

class InventoryBase(BaseModel):
    item_key: str
    name: str
    type: str
    rarity: str
    count: int = 1
    rank: Optional[int] = None
    polarity: Optional[List[str]] = []
    extra: Optional[Dict] = {}

class InventoryCreate(InventoryBase):
    pass


class InventoryInDB(InventoryBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class InventoryPublic(InventoryBase):
    id: str
