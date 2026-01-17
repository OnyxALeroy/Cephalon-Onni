from pydantic import BaseModel, Field
from datetime import datetime
from bson import ObjectId
from typing import Optional, List, Dict, Any

from models.pyobjectid import PyObjectId


class WarframeAbility(BaseModel):
    abilityUniqueName: str
    abilityName: str
    description: str


class WarframeDetails(BaseModel):
    uniqueName: str
    name: str
    parentName: Optional[str]
    description: str
    health: int
    shield: int
    armor: int
    stamina: int
    power: int
    codexSecret: bool
    masteryReq: int
    sprintSpeed: float
    passiveDescription: Optional[str]
    exalted: Optional[List[str]]
    abilities: List[WarframeAbility]
    productCategory: str


class BuildBase(BaseModel):
    name: str
    warframe_uniqueName: str


class BuildCreate(BuildBase):
    pass


class BuildUpdate(BaseModel):
    name: Optional[str] = None
    warframe_uniqueName: Optional[str] = None


class BuildInDB(BuildBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class BuildPublic(BaseModel):
    id: str
    name: str
    warframe_uniqueName: str
    created_at: datetime
    updated_at: datetime
    warframe: Optional[WarframeDetails] = None


class BuildWithDetails(BaseModel):
    id: str
    name: str
    warframe_uniqueName: str
    created_at: datetime
    updated_at: datetime
    warframe: WarframeDetails