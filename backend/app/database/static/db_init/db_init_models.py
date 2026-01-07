from typing import Literal, NotRequired, TypedDict, Union


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


# -------------------------------------------------------------------------------------------------

AnyExportJson = Union[list[Recipe], list[ImgItem]]
AnyExportJsonDirect = Union[dict[str, list[Recipe]], dict[str, list[ImgItem]]]


class ExportJsonDict(TypedDict, total=False):
    ExportRecipes: list[Recipe]
    ExportManifest: list[ImgItem]
    ExportWarframes: list[Warframe]


ExportTypeDictKeys = Literal["ExportRecipes", "ExportManifest", "ExportWarframes"]


# Unused function
def get_exported_json_dict_key(key: str) -> ExportTypeDictKeys:
    if key == "ExportRecipes":
        return ExportTypeDictKeys.ExportRecipes
    elif key == "ExportManifest":
        return ExportTypeDictKeys.ExportManifest
    elif key == "ExportWarframes":
        return ExportTypeDictKeys.ExportWarframes
    else:
        raise ValueError(f"Invalid key: {key}")
