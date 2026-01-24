from datetime import datetime
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, field_validator

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
    @field_validator("name", "warframe_uniqueName", mode="before")
    @classmethod
    def strip_whitespace(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Name cannot be empty")
        return v

    @field_validator("warframe_uniqueName")
    @classmethod
    def warframe_must_not_be_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Warframe selection cannot be empty")
        return v


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

    @field_validator("id")
    @classmethod
    def validate_id(cls, v):
        if not v or not isinstance(v, str):
            raise ValueError("Build ID must be a non-empty string")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        if not v or not isinstance(v, str) or v.strip() == "":
            raise ValueError("Build name must be a non-empty string")
        return v.strip()

    @field_validator("warframe_uniqueName")
    @classmethod
    def validate_warframe_unique_name(cls, v):
        if not v or not isinstance(v, str) or v.strip() == "":
            raise ValueError("Warframe unique name must be a non-empty string")
        return v.strip()

    @field_validator("warframe")
    @classmethod
    def validate_warframe(cls, v):
        if v is not None:
            # Ensure warframe has required fields if present
            if not hasattr(v, "name") or not v.name:
                raise ValueError("Warframe details must have a valid name")
        return v


class BuildWithDetails(BaseModel):
    id: str
    name: str
    warframe_uniqueName: str
    created_at: datetime
    updated_at: datetime
    warframe: WarframeDetails
