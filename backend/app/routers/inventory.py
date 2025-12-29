from fastapi import APIRouter, Request, HTTPException
from bson import ObjectId
from typing import List
from database.dynamic.db import inventories_collection
from models.inventories import InventoryPublic
from routers.user import decode_token

router = APIRouter(prefix="/api/inventory")

def get_user_id(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(401)
    return ObjectId(decode_token(token)["sub"])


@router.get("", response_model=List[InventoryPublic])
def get_inventory(request: Request):

    user_id = get_user_id(request)

    items = inventories_collection.find({"user_id": user_id})

    return [
        {
            "id": str(i["_id"]),
            "name": i["name"],
            "type": i["type"],
            "rarity": i["rarity"],
            "count": i.get("count", 1),
            "rank": i.get("rank"),
            "polarity": i.get("polarity", []),
            "extra": i.get("extra", {})
        }
        for i in items
    ]


@router.get("/{item_id}", response_model=InventoryPublic)
def get_one(item_id: str, request: Request):

    user_id = get_user_id(request)

    item = inventories_collection.find_one({
        "_id": ObjectId(item_id),
        "user_id": user_id
    })

    if not item:
        raise HTTPException(status_code=404)

    return {
        "id": str(item["_id"]),
        "name": item["name"],
        "type": item["type"],
        "rarity": item["rarity"],
        "count": item.get("count", 1),
        "rank": item.get("rank"),
        "polarity": item.get("polarity", []),
        "extra": item.get("extra", {})
    }
