from enum import Enum
from typing import List, Literal, NotRequired, TypedDict

# -------------------------------------------------------------------------------------------------


class RelicReward(TypedDict):
    rewardName: str
    rarity: str
    tier: int
    itemCount: int


class Relic(TypedDict):
    uniqueName: str
    name: str
    codexSecret: bool
    description: str
    relicRewards: List[RelicReward]


class ArcanaLevelStat(TypedDict):
    stats: List[str]


class Arcana(TypedDict):
    uniqueName: str
    name: str
    codexSecret: bool
    rarity: NotRequired[str]
    levelStats: List[ArcanaLevelStat]


# -------------------------------------------------------------------------------------------------


class FetchedMission(TypedDict):
    uniqueName: str
    factionIndex: int
    masteryReq: int
    maxEnemyLevel: int
    minEnemyLevel: int
    missionIndex: int
    name: str
    nodeType: int
    systemIndex: int
    systemName: str


# -------------------------------------------------------------------------------------------------


class ProductCategory(str, Enum):
    MELEE = "Melee"
    OPERATOR_AMPS = "OperatorAmps"
    SPACE_GUNS = "SpaceGuns"
    PISTOLS = "Pistols"
    SPECIAL_ITEMS = "SpecialItems"
    LONG_GUNS = "LongGuns"
    SENTINEL_WEAPONS = "SentinelWeapons"
    SPACE_MELEE = "SpaceMelee"


class Weapon(TypedDict):
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
    productCategory: ProductCategory
    totalDamage: int
    accuracy: NotRequired[float]
    blockingAngle: NotRequired[int]
    comboDuration: NotRequired[int]
    excludeFromCodex: NotRequired[bool]
    followThrough: NotRequired[float]
    heavyAttackDamage: NotRequired[int]
    heavySlamAttack: NotRequired[int]
    heavySlamRadialDamage: NotRequired[int]
    heavySlamRadius: NotRequired[int]
    magazineSize: NotRequired[int]
    maxLevelCap: NotRequired[int]
    multishot: NotRequired[int]
    noise: NotRequired[str]
    primeOmegaAttenuation: NotRequired[float]
    range: NotRequired[float]
    reloadTime: NotRequired[float]
    sentinel: NotRequired[bool]
    slamAttack: NotRequired[int]
    slamRadialDamage: NotRequired[int]
    slamRadius: NotRequired[int]
    slideAttack: NotRequired[int]
    slot: NotRequired[int]
    trigger: NotRequired[str]
    windUp: NotRequired[float]


# -------------------------------------------------------------------------------------------------


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


# -------------------------------------------------------------------------------------------------


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


# -------------------------------------------------------------------------------------------------


class Ingredient(TypedDict):
    ItemType: str
    ItemCount: int


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


# -------------------------------------------------------------------------------------------------


class ImgItem(TypedDict):
    uniqueName: str
    textureLocation: str
