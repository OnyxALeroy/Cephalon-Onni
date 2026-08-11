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


class ModDetails(BaseModel):
    uniqueName: str
    name: str
    polarity: str
    rarity: str
    type: Optional[str]
    subtype: Optional[str]
    codexSecret: bool
    baseDrain: int
    fusionLimit: int
    compatName: Optional[str]
    modSet: Optional[str]
    isUtility: Optional[bool]
    description: Optional[List[str]]


class WeaponDetails(BaseModel):
    uniqueName: str
    name: str
    codexSecret: bool
    criticalChance: float
    criticalMultiplier: float
    damagePerShot: List[int]
    description: str
    fireRate: float
    masteryReq: int
    omegaAttenuation: float
    procChance: float
    productCategory: str
    totalDamage: int
    accuracy: Optional[float]
    magazineSize: Optional[int]
    reloadTime: Optional[float]
    multishot: Optional[int]
    noise: Optional[str]
    trigger: Optional[str]


class ArcaneDetails(BaseModel):
    uniqueName: str
    name: str
    codexSecret: bool
    rarity: Optional[str]
    levelStats: List[dict]


class EquippedMod(BaseModel):
    uniqueName: str
    level: int = Field(default=0, ge=0, le=10)

    @field_validator("uniqueName")
    @classmethod
    def validate_mod_unique_name(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Mod unique name cannot be empty")
        return v.strip()


class WeaponBuild(BaseModel):
    weapon_uniqueName: str
    mods: List[EquippedMod] = Field(default_factory=list, max_length=9)
    arcane_uniqueName: Optional[str] = None

    @field_validator("weapon_uniqueName")
    @classmethod
    def validate_weapon_unique_name(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Weapon unique name cannot be empty")
        return v.strip()

    @field_validator("mods")
    @classmethod
    def validate_mods_length(cls, v):
        if len(v) > 9:
            raise ValueError("Weapon can have maximum 9 mods")
        return v


class BuildBase(BaseModel):
    name: str
    warframe_uniqueName: str
    warframe_mods: List[EquippedMod] = Field(default_factory=list, max_length=10)
    warframe_arcanes: List[str] = Field(default_factory=list, max_length=2)
    primary_weapon: Optional[WeaponBuild] = None
    secondary_weapon: Optional[WeaponBuild] = None
    melee_weapon: Optional[WeaponBuild] = None


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
        return v.strip()

    @field_validator("warframe_mods")
    @classmethod
    def validate_warframe_mods_length(cls, v):
        if len(v) > 10:
            raise ValueError("Warframe can have maximum 10 mods")
        return v

    @field_validator("warframe_arcanes")
    @classmethod
    def validate_warframe_arcanes_length(cls, v):
        if len(v) > 2:
            raise ValueError("Warframe can have maximum 2 arcanes")
        return v


class BuildUpdate(BaseModel):
    name: Optional[str] = None
    warframe_uniqueName: Optional[str] = None
    warframe_mods: Optional[List[EquippedMod]] = None
    warframe_arcanes: Optional[List[str]] = None
    primary_weapon: Optional[WeaponBuild] = None
    secondary_weapon: Optional[WeaponBuild] = None
    melee_weapon: Optional[WeaponBuild] = None


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
    warframe_mods: List[EquippedMod] = []
    warframe_arcanes: List[str] = []
    primary_weapon: Optional[WeaponBuild] = None
    secondary_weapon: Optional[WeaponBuild] = None
    melee_weapon: Optional[WeaponBuild] = None

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
    warframe_mods: List[EquippedMod] = []
    warframe_arcanes: List[ArcaneDetails] = []
    primary_weapon: Optional[WeaponBuild] = None
    secondary_weapon: Optional[WeaponBuild] = None
    melee_weapon: Optional[WeaponBuild] = None
    primary_weapon_details: Optional[WeaponDetails] = None
    secondary_weapon_details: Optional[WeaponDetails] = None
    melee_weapon_details: Optional[WeaponDetails] = None
    primary_arcane_details: Optional[ArcaneDetails] = None
    secondary_arcane_details: Optional[ArcaneDetails] = None
    melee_arcane_details: Optional[ArcaneDetails] = None
