from typing import List

from dependencies import get_current_user_id
from fastapi import APIRouter, HTTPException, Request
from models.inventories import InventoryPublic
from services.inventory_service import InventoryService

router = APIRouter(prefix="/api/inventory")


@router.get("", response_model=List[InventoryPublic])
async def get_inventory(request: Request):
    user_id = get_current_user_id(request)
    return await InventoryService.get_user_inventory(user_id)


@router.get("/{item_id}", response_model=InventoryPublic)
async def get_one(item_id: str, request: Request):
    user_id = get_current_user_id(request)
    item = await InventoryService.get_inventory_item(item_id, user_id)
    if not item:
        raise HTTPException(status_code=404)
    return item
