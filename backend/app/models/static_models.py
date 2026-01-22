from enum import Enum
from typing import List, Literal, NotRequired, TypedDict


class ModType(str, Enum):
    NONE = "---"
    SENTINEL = "SENTINEL"
    PARAZON = "PARAZON"
    WARFRAME = "WARFRAME"
    MELEE = "MELEE"
    ARCHWING = "ARCHWING"
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    KAVAT = "KAVAT"
    STANCE = "STANCE"
    ARCH_GUN = "ARCH-GUN"
    ARCH_MELEE = "ARCH-MELEE"
    HELMINTH_CHARGER = "HELMINTH CHARGER"
    KUBROW = "KUBROW"
    AURA = "AURA"


class ModStat(TypedDict):
    stats: List[str]


class Mod(TypedDict):
    uniqueName: str
    name: str
    polarity: str
    rarity: str
    type: NotRequired[ModType]
    subtype: NotRequired[str]
    codexSecret: bool
    baseDrain: int
    fusionLimit: int
    compatName: NotRequired[
        str
    ]  # Is the mod exclusive to a specific weapon type / Warframe / ...
    modSet: NotRequired[str]
    modSetValues: NotRequired[List[float]]
    isUtility: NotRequired[bool]  # == IsExilus
    description: NotRequired[List[str]]
    levelStats: NotRequired[List[ModStat]]
    upgradeEntries: NotRequired[list]
    availableChallenges: NotRequired[list]


class WarframeAbility(TypedDict):
    abilityUniqueName: str
    abilityName: str
    description: str


class Warframe(TypedDict):
    uniqueName: str
    name: str
    parentName: str
    description: str
    health: int
    shield: int
    armor: int
    stamina: int
    power: int
    codexSecret: bool
    masteryReq: int
    sprintSpeed: float
    passiveDescription: NotRequired[str]
    exalted: NotRequired[list[str]]
    abilities: list[WarframeAbility]
    productCategory: Literal["Suits", "SpaceSuits", "MechSuits"]


class Ingredient(TypedDict):
    ItemType: str
    ItemCount: int


class ImgItem(TypedDict):
    uniqueName: str
    textureLocation: str


class Recipe(TypedDict):
    uniqueName: str
    buildPrice: int
    buildTime: int
    skipBuildTimePrice: int
    consumeOnUse: bool
    num: int
    codexSecret: bool
    resultType: str
    ingredients: list[Ingredient]
