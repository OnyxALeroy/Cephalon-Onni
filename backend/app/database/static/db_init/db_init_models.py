from typing import Literal, TypedDict, Union


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


ExportTypeDictKeys = Literal["ExportRecipes", "ExportManifest"]

# Unused function
def get_exported_json_dict_key(key: str) -> ExportTypeDictKeys:
    if key == "ExportRecipes":
        return ExportTypeDictKeys.ExportRecipes
    elif key == "ExportManifest":
        return ExportTypeDictKeys.ExportManifest
    else:
        raise ValueError(f"Invalid key: {key}")
