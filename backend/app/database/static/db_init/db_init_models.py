from typing import Literal, NotRequired, TypedDict


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
